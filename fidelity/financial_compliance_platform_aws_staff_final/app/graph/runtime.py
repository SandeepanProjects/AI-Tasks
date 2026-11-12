from datetime import datetime, timedelta, timezone
from uuid import uuid4
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from sqlalchemy import select
from app.config import settings
from app.db.session import Session
from app.db.models import Review, AuditEvent
from app.security.tenant_context import set_tenant_context
from app.retrieval.ingestion import get_embedder
from app.retrieval.strategies import KeywordStrategy, VectorStrategy, HybridStrategy
from app.graph.workflow import Workflow
from app.domain.schemas import ReviewStatus
from app.domain.state_machine import assert_transition
from langgraph.types import Command

async def _loader(tenant_id, query):
    async with Session() as db:
        await set_tenant_context(db, tenant_id)
        keyword = KeywordStrategy()
        try:
            strategy = HybridStrategy(VectorStrategy(get_embedder()), keyword)
        except RuntimeError:
            strategy = keyword
        rows = await strategy.retrieve(db, tenant_id, query, 6)
        return [{"id": p.id, "tenant_id": p.tenant_id, "code": p.code,
                 "version": p.version, "title": p.title, "text": p.text} for p in rows]

def _thread(tenant_id, review_id):
    return f"tenant:{tenant_id}:review:{review_id}"

async def _claim_review(tenant_id: str, review_id: str, decision: bool, task_id: str | None) -> tuple[bool, str | None, str | None]:
    async with Session() as db:
        async with db.begin():
            await set_tenant_context(db, tenant_id)
            review = await db.scalar(select(Review).where(
                Review.id == review_id, Review.tenant_id == tenant_id).with_for_update())
            if not review:
                raise LookupError("Review not found")
            expected = ReviewStatus.DECISION_QUEUED if decision else ReviewStatus.QUEUED
            target = ReviewStatus.RESUMING if decision else ReviewStatus.RUNNING
            same_task_redelivery = review.status == target.value and task_id is not None and review.worker_task_id == task_id
            lease_expired = not review.worker_lease_until or review.worker_lease_until <= datetime.now(timezone.utc)
            if review.status == target.value and not same_task_redelivery and not lease_expired:
                return False, review.input_text, review.thread_id
            if review.status != expected.value and not (review.status == target.value and (same_task_redelivery or lease_expired)):
                return False, review.input_text, review.thread_id
            if review.status == expected.value:
                assert_transition(review.status, target)
            review.status = target.value
            review.worker_lease_until = datetime.now(timezone.utc) + timedelta(minutes=5)
            review.worker_task_id = task_id
            return True, review.input_text, review.thread_id

async def invoke_review(tenant_id, review_id, decision=None, task_id=None):
    claimed, statement, thread_id = await _claim_review(tenant_id, review_id, decision is not None, task_id)
    if not claimed:
        return {"review_id": review_id, "status": "already_claimed_or_terminal"}
    pool = AsyncConnectionPool(conninfo=settings.sync_database_url, min_size=1, max_size=4, open=False)
    await pool.open()
    try:
        async with AsyncPostgresSaver(pool) as checkpointer:
            await checkpointer.setup()
            workflow = Workflow(_loader, checkpointer)
            config = {"configurable": {"thread_id": thread_id or _thread(tenant_id, review_id)}}
            # If the graph reached a durable pause/final checkpoint but the
            # worker died before updating the Review row, persist that checkpoint
            # instead of replaying LLM/tool work or resuming an already-finished HITL.
            snapshot = await workflow.graph.aget_state(config)
            snapshot_values = snapshot.values if snapshot and snapshot.values else {}
            snapshot_status = snapshot_values.get("status")
            if decision is not None and snapshot_status in {"approved", "rejected", "failed"}:
                result = snapshot_values
            elif decision is None and snapshot_status in {"needs_human", "failed"} and (snapshot_status == "failed" or snapshot.next):
                result = snapshot_values
            elif decision is None:
                result = await workflow.graph.ainvoke({
                    "review_id": review_id, "tenant_id": tenant_id, "statement": statement,
                    "max_steps": settings.max_agent_steps,
                    "max_reworks": settings.max_evaluation_reworks,
                }, config=config)
            else:
                result = await workflow.graph.ainvoke(Command(resume=decision), config=config)
            async with Session() as db:
                async with db.begin():
                    await set_tenant_context(db, tenant_id)
                    review = await db.scalar(select(Review).where(
                        Review.id == review_id, Review.tenant_id == tenant_id).with_for_update())
                    if review:
                        new_status = result.get("status", "failed")
                        if review.status != new_status:
                            assert_transition(review.status, new_status)
                        review.status = new_status
                        review.result_json = result.get("final_result")
                        review.worker_lease_until = None
                        review.worker_task_id = None
                        db.add(AuditEvent(id=uuid4().hex, tenant_id=tenant_id, review_id=review_id,
                            actor_id=(decision or {}).get("actor_id", "system"),
                            event_type=f"review.{new_status}", details={"rework_count": result.get("rework", 0)}))
            return {"review_id": review_id, "status": result.get("status", "failed")}
    except Exception:
        # Expire the lease so Celery redelivery can resume from the durable graph checkpoint.
        async with Session() as db:
            async with db.begin():
                await set_tenant_context(db, tenant_id)
                review = await db.scalar(select(Review).where(Review.id == review_id, Review.tenant_id == tenant_id).with_for_update())
                if review:
                    review.worker_lease_until = datetime.now(timezone.utc) - timedelta(seconds=1)
        raise
    finally:
        await pool.close()

async def mark_review_failed(tenant_id: str, review_id: str, actor_id: str = "system"):
    """Persist terminal failure after Celery exhausts its retry budget."""
    async with Session() as db:
        async with db.begin():
            await set_tenant_context(db, tenant_id)
            review = await db.scalar(select(Review).where(
                Review.id == review_id, Review.tenant_id == tenant_id).with_for_update())
            if not review or review.status in {ReviewStatus.APPROVED.value, ReviewStatus.REJECTED.value, ReviewStatus.FAILED.value}:
                return
            assert_transition(review.status, ReviewStatus.FAILED)
            review.status = ReviewStatus.FAILED.value
            review.worker_lease_until = None
            review.worker_task_id = None
            db.add(AuditEvent(id=uuid4().hex, tenant_id=tenant_id, review_id=review_id,
                actor_id=actor_id, event_type="review.failed", details={"reason": "worker_retry_exhausted"}))
