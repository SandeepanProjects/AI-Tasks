from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException
from app.application.schemas import CreateReviewRequest, ReviewCreated, ReviewDecision, ReviewView
from app.application.use_cases import ReviewService
from app.api.dependencies import get_review_repository, get_audit_repository
from app.core.security import Principal, Role, current_principal, require_role
from app.core.errors import DomainError
from app.workers.tasks import process_review

router=APIRouter(prefix="/reviews",tags=["reviews"])

def build_service(repo,audit):
    from app.application.workflow_factory import build_workflow
    return ReviewService(repo,build_workflow(),audit)

@router.post("",response_model=ReviewCreated,status_code=202)
async def create_review(body:CreateReviewRequest,
    principal:Principal=Depends(require_role(Role.ANALYST,Role.REVIEWER,Role.ADMIN)),
    repo=Depends(get_review_repository), audit=Depends(get_audit_repository),
    idempotency_key:str=Header(...,alias="Idempotency-Key")):
    try:
        review=await build_service(repo,audit).create(principal,body.question,body.scope.assets,
                    body.scope.lookback_days,body.purpose,idempotency_key)
        process_review.delay(str(review.id))
        return ReviewCreated(review_id=review.id,status=review.status.value)
    except DomainError as exc: raise HTTPException(exc.status_code,detail={"code":exc.code,"message":str(exc)})

@router.get("/{review_id}",response_model=ReviewView)
async def get_review(review_id:UUID,principal:Principal=Depends(current_principal),repo=Depends(get_review_repository)):
    try:
        r=await repo.get(principal.tenant_id,review_id)
        if not r: raise DomainError("Review not found")
        return ReviewView(review_id=r.id,status=r.status.value,report=r.report,reviewer_comment=r.reviewer_comment)
    except DomainError as exc: raise HTTPException(404,str(exc))

@router.post("/{review_id}/decision",response_model=ReviewView)
async def decide(review_id:UUID,body:ReviewDecision,
    principal:Principal=Depends(current_principal),repo=Depends(get_review_repository),
    audit=Depends(get_audit_repository)):
    try:
        r=await build_service(repo,audit).decide(principal,review_id,body.decision,body.comment)
        return ReviewView(review_id=r.id,status=r.status.value,report=r.report,reviewer_comment=r.reviewer_comment)
    except DomainError as exc: raise HTTPException(exc.status_code,detail={"code":exc.code,"message":str(exc)})
