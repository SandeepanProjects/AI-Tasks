from uuid import uuid4
from app.models.review import Review
from app.models.audit import AuditEvent
from app.graph.workflow import run_compliance_graph
class ReviewService:
    async def create(self,db,tenant_id,actor,content):
        row=Review(id=str(uuid4()),tenant_id=tenant_id,submitted_by=actor,content=content,status="queued")
        db.add(row); db.add(AuditEvent(tenant_id=tenant_id,review_id=row.id,actor=actor,action="review_created",details={}))
        await db.commit(); await db.refresh(row); return row
    async def run(self,db,row):
        row.status="processing"; await db.commit()
        try:
            state=await run_compliance_graph(row.id,row.tenant_id,row.content,db)
            row.result=state["result"]; row.status="pending_approval"
            db.add(AuditEvent(tenant_id=row.tenant_id,review_id=row.id,actor="system",action="analysis_completed",details={"risk":row.result.get("overall_risk")}))
        except Exception as exc:
            row.status="failed"; db.add(AuditEvent(tenant_id=row.tenant_id,review_id=row.id,actor="system",action="analysis_failed",details={"error_type":type(exc).__name__})); await db.commit(); raise
        await db.commit(); await db.refresh(row); return row
    async def decide(self,db,row,actor,decision,comment):
        if row.status!="pending_approval": raise ValueError("Only pending_approval reviews can be decided")
        row.status=decision; row.decided_by=actor; row.decision_comment=comment
        db.add(AuditEvent(tenant_id=row.tenant_id,review_id=row.id,actor=actor,action=f"review_{decision}",details={"comment":comment}))
        await db.commit(); await db.refresh(row); return row
review_service=ReviewService()
