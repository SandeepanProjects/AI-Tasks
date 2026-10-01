from uuid import uuid4
from app.db.models import Review, Policy
from app.repositories.sqlalchemy import SqlReviewRepository, SqlPolicyRepository
from app.retrieval.strategies import KeywordStrategy
from app.graph.workflow import Workflow
from app.domain.schemas import ReviewStatus
from app.domain.transitions import validate_transition
from app.config import settings


class ReviewService:
    def __init__(self, db):
        self.db = db
        self.reviews = SqlReviewRepository(db)
        self.policies = SqlPolicyRepository(db)

        async def loader(tenant, query):
            rows = await KeywordStrategy().retrieve(db, tenant, query, 6)
            return [
                {
                    "id": p.id,
                    "tenant_id": p.tenant_id,
                    "code": p.code,
                    "version": p.version,
                    "title": p.title,
                    "text": p.text,
                }
                for p in rows
            ]

        self.workflow = Workflow(
            loader, settings.max_agent_steps, settings.max_evaluation_reworks
        )

    async def create(self, tenant, actor, statement):
        rid = uuid4().hex
        obj = Review(
            id=rid,
            tenant_id=tenant,
            created_by=actor,
            status="queued",
            input_text=statement,
            result_json=None,
            thread_id=rid,
        )
        await self.reviews.add(obj)
        return obj

    async def run(self, tenant, rid):
        obj = await self.reviews.get(tenant, rid)
        if not obj:
            raise LookupError("Review not found")
        validate_transition(ReviewStatus(obj.status), ReviewStatus.RUNNING)
        obj.status = "running"
        await self.reviews.save(obj)
        state = await self.workflow.graph.ainvoke(
            {
                "review_id": rid,
                "tenant_id": tenant,
                "statement": obj.input_text,
                "max_steps": settings.max_agent_steps,
                "max_reworks": settings.max_evaluation_reworks,
            }
        )
        obj.status = state.get("status", "failed")
        obj.result_json = state.get("final_result")
        await self.reviews.save(obj)
        return obj

    async def decide(self, tenant, rid, actor, decision, comment):
        obj = await self.reviews.get(tenant, rid)
        if not obj:
            raise LookupError("Review not found")
        if obj.status != "needs_human":
            raise ValueError("Review is not awaiting human decision")
        target = {
            "approve": ReviewStatus.APPROVED,
            "reject": ReviewStatus.REJECTED,
            "request_changes": ReviewStatus.NEEDS_HUMAN,
        }[decision]
        if target == ReviewStatus.NEEDS_HUMAN:
            raise ValueError("Request-changes requires a separate revision workflow")
        validate_transition(ReviewStatus(obj.status), target)
        obj.status = target.value
        obj.result_json = {
            **(obj.result_json or {}),
            "human_decision": {
                "decision": decision,
                "comment": comment,
                "actor_id": actor,
            },
        }
        await self.reviews.save(obj)
        return obj
