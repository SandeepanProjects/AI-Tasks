import asyncio
from sqlalchemy import select
from app.worker.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.review import Review
from app.services.review_service import review_service
@celery_app.task(name="app.worker.tasks.run_review_task")
def run_review_task(review_id,tenant_id): return asyncio.run(_run(review_id,tenant_id))
async def _run(rid,tenant):
    async with SessionLocal() as db:
        row=(await db.execute(select(Review).where(Review.id==rid,Review.tenant_id==tenant))).scalar_one_or_none()
        if not row: return {"status":"not_found"}
        if row.status not in ("queued","failed"): return {"status":row.status}
        result=await review_service.run(db,row); return {"review_id":result.id,"status":result.status}
