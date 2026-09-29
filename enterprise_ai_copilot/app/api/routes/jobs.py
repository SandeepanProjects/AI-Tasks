from fastapi import APIRouter, Depends, HTTPException
from celery.result import AsyncResult

from app.api.dependencies import Principal, get_current_principal
from app.core.database import get_db
from app.repositories.job_repository import JobRepository
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/{job_id}")
async def get_job(
    job_id: str,
    principal: Principal = Depends(get_current_principal),
    db=Depends(get_db),
):
    job = await JobRepository(db).get_for_tenant(job_id, principal.tenant_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = AsyncResult(job.celery_task_id, app=celery_app)
    return {
        "job_id": job.id,
        "type": job.job_type,
        "status": result.status,
        "result": result.result if result.successful() else None,
        "error": str(result.result) if result.failed() else None,
    }
