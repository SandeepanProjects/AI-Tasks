from celery import Celery
import os

celery = Celery(
    "compliance",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
)
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery.task(
    bind=True,
    max_retries=3,
    autoretry_for=(TimeoutError, ConnectionError),
    retry_backoff=True,
    retry_jitter=True,
)
def run_review(self, tenant_id, review_id):
    import asyncio
    from app.db.session import Session
    from app.services.review_service import ReviewService

    async def work():
        async with Session() as db:
            return await ReviewService(db).run(tenant_id, review_id)

    obj = asyncio.run(work())
    return {"review_id": obj.id, "status": obj.status}
