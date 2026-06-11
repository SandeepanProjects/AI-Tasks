from app.scaling.queue.celery_app import celery_app
from app.rag.ingestion.ingest_service import IngestionService


@celery_app.task
def ingest_document_task(file_path: str):

    service = IngestionService()

    return service.ingest(file_path)