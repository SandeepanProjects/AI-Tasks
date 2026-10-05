import asyncio
from uuid import UUID
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.adapters.repositories import SqlReviewRepository, SqlAuditRepository
from app.application.workflow_factory import build_workflow
from app.domain.models import ReviewStatus
from app.core.metrics import REVIEW_JOBS

async def _process(review_id:str):
    async with SessionLocal() as session:
        repo=SqlReviewRepository(session); audit=SqlAuditRepository(session)
        # Tenant is read from durable row; worker does not trust queue payload for authorization.
        from sqlalchemy import select
        from app.db.models import ReviewRow
        row=await session.scalar(select(ReviewRow).where(ReviewRow.id==UUID(review_id)))
        if not row: return
        review=await repo.get(row.tenant_id,UUID(review_id))
        if not review or review.status != ReviewStatus.QUEUED: return
        review.transition(ReviewStatus.RUNNING); await repo.save(review,review.version-1)
        try:
            report=await build_workflow().run(review)
            review=await repo.get(row.tenant_id,UUID(review_id))
            review.report=report; review.transition(ReviewStatus.AWAITING_REVIEW)
            await repo.save(review,review.version-1)
            await audit.append(review.tenant_id,"system","review.completed",str(review.id),{})
            REVIEW_JOBS.labels("success").inc()
        except Exception as exc:
            review=await repo.get(row.tenant_id,UUID(review_id))
            if review and review.status==ReviewStatus.RUNNING:
                review.transition(ReviewStatus.FAILED); await repo.save(review,review.version-1)
            await audit.append(row.tenant_id,"system","review.failed",review_id,{"error_type":type(exc).__name__})
            REVIEW_JOBS.labels("failed").inc()
            raise

@celery_app.task(bind=True,name="app.workers.tasks.process_review",autoretry_for=(TimeoutError,),
                retry_backoff=True,retry_jitter=True,max_retries=3)
def process_review(self,review_id:str):
    return asyncio.run(_process(review_id))
