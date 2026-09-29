from celery import Celery
from app.config import settings

celery = Celery(
    "compliance",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    task_routes={
        "reviews.execute": {"queue": "reviews"},
        "reviews.resume": {"queue": "reviews"},
    },
)
