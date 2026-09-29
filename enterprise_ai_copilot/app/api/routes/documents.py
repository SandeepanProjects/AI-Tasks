import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import Principal, get_current_principal
from app.core.database import get_db
from app.models.job import Job
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentResponse
from app.workers.tasks import process_document

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", response_model=DocumentResponse)
async def create_document(
    request: DocumentCreate,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    document = await DocumentRepository(db).create(
        principal.tenant_id, request.title, request.content
    )
    await db.commit()
    await db.refresh(document)
    return DocumentResponse(
        id=document.id, title=document.title, status=document.status
    )

@router.post("/{document_id}/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    document_id: str,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    document = await DocumentRepository(db).get_for_tenant(
        document_id, principal.tenant_id
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    task = process_document.delay(document_id)
    job = Job(
        id=str(uuid.uuid4()),
        tenant_id=principal.tenant_id,
        celery_task_id=task.id,
        job_type="document_ingestion",
        status="queued",
    )
    db.add(job)
    await db.commit()

    return {
        "job_id": job.id,
        "celery_task_id": task.id,
        "status": "queued",
    }
