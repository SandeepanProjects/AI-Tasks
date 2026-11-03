from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException
from app.application.schemas import CreateReviewRequest, ReviewCreated, ReviewDecision, ReviewView
from app.application.use_cases import ReviewService
from app.api.dependencies import get_review_repository
from app.core.security import Principal, Role, current_principal, require_role
from app.core.errors import DomainError
from app.workers.tasks import process_review
import structlog

logger = structlog.get_logger(__name__)

router=APIRouter(prefix="/reviews",tags=["reviews"])

def build_service(repo):
    # HTTP handlers do not instantiate LLM/embedding clients; workers own execution.
    return ReviewService(repo)

@router.post("",response_model=ReviewCreated,status_code=202)
async def create_review(body:CreateReviewRequest,
    principal:Principal=Depends(require_role(Role.ANALYST,Role.REVIEWER,Role.ADMIN)),
    repo=Depends(get_review_repository),
    idempotency_key:str=Header(...,alias="Idempotency-Key",min_length=8,max_length=256)):
    try:
        review=await build_service(repo).create(principal,body.question,body.scope.assets,
                    body.scope.lookback_days,body.purpose,idempotency_key)
        # Outbox event was committed atomically with the review. Best-effort fast dispatch;
        # the scheduled outbox publisher recovers if Redis is unavailable here.
        try:
            process_review.delay(str(review.id), review.tenant_id)
        except Exception as exc:
            # The committed outbox event is the recovery path; do not fail an already-created request.
            logger.warning("fast_task_dispatch_failed", review_id=str(review.id), error_type=type(exc).__name__)
        return ReviewCreated(review_id=review.id,status=review.status.value)
    except DomainError as exc: raise HTTPException(exc.status_code,detail={"code":exc.code,"message":str(exc)})

@router.get("/{review_id}",response_model=ReviewView)
async def get_review(review_id:UUID,principal:Principal=Depends(current_principal),repo=Depends(get_review_repository)):
    try:
        r=await repo.get(principal.tenant_id,review_id)
        if not r: raise DomainError("Review not found")
        can_view_unapproved = bool(principal.roles.intersection({Role.REVIEWER, Role.ADMIN}))
        visible_report = r.report if r.status.value == "approved" or can_view_unapproved else None
        return ReviewView(review_id=r.id,status=r.status.value,report=visible_report,reviewer_comment=r.reviewer_comment)
    except DomainError as exc: raise HTTPException(404,str(exc))

@router.post("/{review_id}/decision",response_model=ReviewView)
async def decide(review_id:UUID,body:ReviewDecision,
    principal:Principal=Depends(current_principal),repo=Depends(get_review_repository)):
    try:
        r=await build_service(repo).decide(principal,review_id,body.decision,body.comment)
        return ReviewView(review_id=r.id,status=r.status.value,report=r.report,reviewer_comment=r.reviewer_comment)
    except DomainError as exc: raise HTTPException(exc.status_code,detail={"code":exc.code,"message":str(exc)})


@router.post("/{review_id}/retry", response_model=ReviewCreated, status_code=202)
async def retry_review(review_id: UUID,
    principal: Principal = Depends(require_role(Role.ADMIN)),
    repo=Depends(get_review_repository)):
    try:
        review = await build_service(repo).retry_failed(principal, review_id)
        try:
            process_review.delay(str(review.id), review.tenant_id)
        except Exception as exc:
            logger.warning("fast_retry_dispatch_failed", review_id=str(review.id), error_type=type(exc).__name__)
        return ReviewCreated(review_id=review.id, status=review.status.value)
    except DomainError as exc:
        raise HTTPException(exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
