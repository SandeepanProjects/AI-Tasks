from celery import Celery
from app.core.config import settings

celery_app = Celery("investment_platform", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json", result_serializer="json", accept_content=["json"],
    task_acks_late=True, worker_prefetch_multiplier=1,
    task_time_limit=300, task_soft_time_limit=270,
    task_routes={"app.workers.tasks.ingest_source": {"queue": "ingestion"}},
)
