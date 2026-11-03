import asyncio
from uuid import UUID
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.adapters.repositories import SqlReviewRepository
from app.application.workflow_factory import build_workflow
from app.domain.models import ReviewStatus
from app.core.metrics import REVIEW_JOBS
import httpx

async def _process(review_id:str, tenant_id:str, retries_exhausted: bool = False):
    async with SessionLocal() as session:
        repo=SqlReviewRepository(session)
        # Queue payload carries the tenant scope; the worker applies RLS and verifies both IDs against the row.
        from sqlalchemy import select, text, update
        from app.db.models import ReviewRow
        # Tenant context must be set before querying an RLS-protected table.
        await session.execute(text("SELECT set_config('app.tenant_id', :tenant_id, true)"), {"tenant_id": tenant_id})
        row=await session.scalar(select(ReviewRow).where(ReviewRow.id==UUID(review_id), ReviewRow.tenant_id==tenant_id))
        if not row:
            async with SessionLocal() as outbox_session:
                from app.adapters.repositories import SqlOutboxRepository
                await SqlOutboxRepository(outbox_session).mark_completed(UUID(review_id))
            return
        review=await repo.get(tenant_id,UUID(review_id))
        if not review or review.status not in {ReviewStatus.QUEUED, ReviewStatus.RUNNING}:
            async with SessionLocal() as outbox_session:
                from app.adapters.repositories import SqlOutboxRepository
                await SqlOutboxRepository(outbox_session).mark_completed(UUID(review_id))
            return
        # Atomic claim prevents concurrent duplicate delivery. A RUNNING row is reclaimable
        # only after its 10-minute lease expires (e.g. worker process was killed).
        from sqlalchemy import or_, func
        claimable = or_(ReviewRow.status == ReviewStatus.QUEUED.value,
            (ReviewRow.status == ReviewStatus.RUNNING.value) &
            (or_(ReviewRow.processing_started_at.is_(None),
                 ReviewRow.processing_started_at < func.now() - text("INTERVAL '10 minutes'"))))
        claimed = await session.execute(update(ReviewRow).where(ReviewRow.id == UUID(review_id),
            ReviewRow.tenant_id == tenant_id, claimable).values(status=ReviewStatus.RUNNING.value,
            version=ReviewRow.version + 1, processing_started_at=func.now()))
        await session.commit()
        if claimed.rowcount != 1: return
        review=await repo.get(tenant_id,UUID(review_id))
        try:
            from app.core.metrics import REVIEW_LATENCY
            with REVIEW_LATENCY.time():
                report=await build_workflow().run(review)
            review=await repo.get(tenant_id,UUID(review_id))
            review.report=report; review.transition(ReviewStatus.AWAITING_REVIEW)
            await repo.save_with_audit(review, expected_version=review.version - 1,
                actor_id="system", action="review.completed", details={})
            async with SessionLocal() as outbox_session:
                from app.adapters.repositories import SqlOutboxRepository
                await SqlOutboxRepository(outbox_session).mark_completed(review.id)
            REVIEW_JOBS.labels("success").inc()
        except Exception as exc:
            review=await repo.get(tenant_id,UUID(review_id))
            transient = (isinstance(exc, (TimeoutError, httpx.TimeoutException, httpx.TransportError)) or
                (isinstance(exc, httpx.HTTPStatusError) and
                 (exc.response.status_code == 429 or exc.response.status_code >= 500)))
            if review and review.status == ReviewStatus.RUNNING:
                if transient and not retries_exhausted:
                    # Release the claim so a Celery retry can atomically claim it again.
                    await session.execute(update(ReviewRow).where(ReviewRow.id == UUID(review_id),
                        ReviewRow.tenant_id == tenant_id, ReviewRow.status == ReviewStatus.RUNNING.value)
                        .values(status=ReviewStatus.QUEUED.value, version=ReviewRow.version + 1, processing_started_at=None))
                    from app.db.models import AuditEventRow
                    session.add(AuditEventRow(tenant_id=tenant_id, actor_id="system",
                        action="review.retry_scheduled", resource_id=review_id,
                        details={"error_type": type(exc).__name__}))
                    await session.commit()
                else:
                    review.transition(ReviewStatus.FAILED)
                    await repo.save_with_audit(review, expected_version=review.version - 1,
                        actor_id="system", action="review.failed",
                        details={"error_type": type(exc).__name__})
            if not transient or retries_exhausted:
                async with SessionLocal() as outbox_session:
                    from app.adapters.repositories import SqlOutboxRepository
                    await SqlOutboxRepository(outbox_session).mark_completed(UUID(review_id))
                REVIEW_JOBS.labels("failed").inc()
            raise

def _run_in_fresh_event_loop(coro):
    """Celery tasks use a fresh asyncio loop; dispose pooled async connections before loop teardown."""
    async def runner():
        try:
            return await coro
        finally:
            from app.db.session import engine
            await engine.dispose()
    return asyncio.run(runner())


@celery_app.task(bind=True,name="app.workers.tasks.process_review",max_retries=3)
def process_review(self,review_id:str, tenant_id:str):
    exhausted = self.request.retries >= self.max_retries
    try:
        return _run_in_fresh_event_loop(_process(review_id, tenant_id, retries_exhausted=exhausted))
    except Exception as exc:
        retryable = (isinstance(exc, (TimeoutError, httpx.TimeoutException, httpx.TransportError)) or
            (isinstance(exc, httpx.HTTPStatusError) and
             (exc.response.status_code == 429 or exc.response.status_code >= 500)))
        if not retryable or exhausted:
            raise
        raise self.retry(exc=exc, countdown=min(60, 2 ** (self.request.retries + 1)))


@celery_app.task(name="app.workers.tasks.publish_outbox")
def publish_outbox():
    async def _publish():
        from app.adapters.repositories import SqlOutboxRepository
        async with SessionLocal() as session:
            repo = SqlOutboxRepository(session)
            events = await repo.pending(limit=100)
            for event in events:
                try:
                    process_review.delay(event.payload["review_id"], event.payload["tenant_id"])
                    await repo.mark_published(event.id)
                except Exception:
                    await repo.mark_attempt(event.id)
    return _run_in_fresh_event_loop(_publish())
