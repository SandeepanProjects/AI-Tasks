from fastapi import APIRouter,Depends
from sqlalchemy import select
from app.db.session import get_db
from app.models.policy import PolicyChunk
from app.schemas.policy import PolicyCreate
from app.rag.ingestion import ingest_policy
from app.auth.dependencies import Principal,require_roles
router=APIRouter(prefix="/policies",tags=["policies"])
@router.post("",status_code=201)
async def create_policy(p:PolicyCreate,db=Depends(get_db),u:Principal=Depends(require_roles("admin"))):
    rows=await ingest_policy(db,u.tenant_id,p.policy_code,p.title,p.text); return {"created_chunks":len(rows),"ids":[r.id for r in rows]}
@router.post("/seed")
async def seed(db=Depends(get_db),u:Principal=Depends(require_roles("admin"))):
    samples=[("ADV-001","Performance claims","Past performance does not guarantee future results. Performance claims must be accurate, balanced, and supported."),("RISK-002","Risk disclosure","Do not describe investments as risk-free or guaranteed unless an approved guarantee applies. Disclose material risks."),("FEES-003","Fees and costs","Fees, expenses, and material costs must be disclosed clearly and not obscured.")]
    count=0
    for code,title,body in samples:
        exists=(await db.execute(select(PolicyChunk.id).where(PolicyChunk.tenant_id==u.tenant_id,PolicyChunk.policy_code==code))).first()
        if not exists: count+=len(await ingest_policy(db,u.tenant_id,code,title,body))
    return {"created_chunks":count,"tenant_id":u.tenant_id}
@router.get("")
async def list_policies(db=Depends(get_db),u:Principal=Depends(require_roles("admin","reviewer","approver"))):
    rows=(await db.execute(select(PolicyChunk).where(PolicyChunk.tenant_id==u.tenant_id))).scalars().all()
    return [{"id":r.id,"policy_code":r.policy_code,"title":r.title,"text":r.text} for r in rows]
