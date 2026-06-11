from celery import Celery


celery_app = Celery(
    "rag_system",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)