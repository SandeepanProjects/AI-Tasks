from celery import Celery

def create_celery(name: str, broker_url: str, result_backend: str | None = None) -> Celery:
    app = Celery(name, broker=broker_url, backend=result_backend)
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        task_track_started=True,
    )
    return app
