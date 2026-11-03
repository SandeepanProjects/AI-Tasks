import asyncio
from celery.utils.log import get_task_logger
from app.workers.celery_app import celery
from app.graph.runtime import invoke_review, mark_review_failed

logger = get_task_logger(__name__)


@celery.task(
    name="reviews.execute",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3, retry_backoff_max=60,
)
def execute_review(self, tenant_id: str, review_id: str):
    try:
        return asyncio.run(invoke_review(tenant_id, review_id, task_id=self.request.id))
    except Exception:
        logger.exception("review execution failed", extra={"review_id": review_id})
        if self.request.retries >= self.max_retries:
            asyncio.run(mark_review_failed(tenant_id, review_id))
        raise


@celery.task(
    name="reviews.resume",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3, retry_backoff_max=60,
)
def resume_review(self, tenant_id: str, review_id: str, decision: dict):
    try:
        return asyncio.run(invoke_review(tenant_id, review_id, decision, task_id=self.request.id))
    except Exception:
        logger.exception("review resume failed", extra={"review_id": review_id})
        if self.request.retries >= self.max_retries:
            asyncio.run(mark_review_failed(tenant_id, review_id))
        raise
