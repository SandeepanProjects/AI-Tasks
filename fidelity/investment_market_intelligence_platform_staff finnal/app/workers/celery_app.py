from celery import Celery
from app.core.config import settings
celery_app=Celery("investment_platform",broker=settings.redis_url,backend=settings.redis_url)
celery_app.conf.update(imports=("app.workers.tasks",), task_serializer="json",result_serializer="json",accept_content=["json"],
    task_acks_late=True,task_reject_on_worker_lost=True,worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True, timezone="UTC", enable_utc=True,
    worker_max_tasks_per_child=1000,
    task_time_limit=300,task_soft_time_limit=270,
    task_routes={"app.workers.tasks.process_review":{"queue":"reviews"},
                 "app.workers.tasks.publish_outbox":{"queue":"outbox"}},
    beat_schedule={})

celery_app.conf.beat_schedule = {
    "publish-review-outbox-every-10-seconds": {
        "task": "app.workers.tasks.publish_outbox",
        "schedule": 10.0,
        "options": {"queue": "outbox"},
    }
}
