import asyncio
from celery.utils.log import get_task_logger
from app.workers.celery_app import celery
from app.graph.runtime import invoke_review

logger = get_task_logger(__name__)


@celery.task(
    name="reviews.execute",
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def execute_review(self, tenant_id: str, review_id: str):
    try:
        return asyncio.run(invoke_review(tenant_id, review_id))
    except Exception:
        logger.exception("review execution failed", extra={"review_id": review_id})
        raise


@celery.task(
    name="reviews.resume",
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def resume_review(self, tenant_id: str, review_id: str, decision: dict):
    try:
        return asyncio.run(invoke_review(tenant_id, review_id, decision))
    except Exception:
        logger.exception("review resume failed", extra={"review_id": review_id})
        raise
