from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from app.db.session import get_db
from app.models.review import Review
from app.models.audit import AuditEvent
from app.schemas.review import ReviewCreate,DecisionRequest
from app.services.review_service import review_service
from app.auth.dependencies import Principal,require_roles
from app.worker.tasks import run_review_task
router=APIRouter(prefix="/reviews",tags=["reviews"])
async def find_review(db,rid,tenant):
    row=(await db.execute(select(Review).where(Review.id==rid,Review.tenant_id==tenant))).scalar_one_or_none()
    if not row: raise HTTPException(404,"Review not found")
    return row
@router.post("",status_code=201)
async def create(p:ReviewCreate,db=Depends(get_db),u:Principal=Depends(require_roles("admin","reviewer"))): return await review_service.create(db,u.tenant_id,u.subject,p.content)
@router.post("/{rid}/run")
async def run(rid:str,db=Depends(get_db),u:Principal=Depends(require_roles("admin","reviewer"))):
    row=await find_review(db,rid,u.tenant_id)
    if row.status not in ("queued","failed"): raise HTTPException(409,f"Cannot run status {row.status}")
    return await review_service.run(db,row)
@router.post("/{rid}/enqueue",status_code=202)
async def enqueue(rid:str,db=Depends(get_db),u:Principal=Depends(require_roles("admin","reviewer"))):
    row=await find_review(db,rid,u.tenant_id)
    if row.status not in ("queued","failed"): raise HTTPException(409,f"Cannot enqueue status {row.status}")
    task=run_review_task.delay(rid,u.tenant_id); return {"task_id":task.id,"status":"enqueued"}
@router.get("/{rid}")
async def read(rid:str,db=Depends(get_db),u:Principal=Depends(require_roles("admin","reviewer","approver"))): return await find_review(db,rid,u.tenant_id)
@router.get("/{rid}/audit")
async def audit(rid:str,db=Depends(get_db),u:Principal=Depends(require_roles("admin","reviewer","approver"))):
    await find_review(db,rid,u.tenant_id)
    rows=(await db.execute(select(AuditEvent).where(AuditEvent.review_id==rid,AuditEvent.tenant_id==u.tenant_id).order_by(AuditEvent.id))).scalars().all()
    return [{"id":r.id,"actor":r.actor,"action":r.action,"details":r.details,"created_at":r.created_at} for r in rows]
@router.post("/{rid}/decision")
async def decision(rid:str,p:DecisionRequest,db=Depends(get_db),u:Principal=Depends(require_roles("admin","approver"))):
    row=await find_review(db,rid,u.tenant_id)
    try: return await review_service.decide(db,row,u.subject,p.decision,p.comment)
    except ValueError as e: raise HTTPException(409,str(e))
