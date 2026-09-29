from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.application.schemas import CreateReviewRequest, ReviewCreated, ReviewDecision, ReviewView
from app.application.use_cases import ReviewService
from app.api.dependencies import get_review_service
from app.core.security import Principal, Role, current_principal, require_role
from app.core.errors import DomainError

router = APIRouter()

@router.post("/reviews", response_model=ReviewCreated, status_code=202)
async def create_review(body: CreateReviewRequest,
                        principal: Principal = Depends(require_role(Role.ANALYST, Role.REVIEWER, Role.ADMIN)),
                        service: ReviewService = Depends(get_review_service)):
    try:
        review = await service.create(principal, body.question, body.scope.assets, body.scope.lookback_days)
        return ReviewCreated(review_id=review.id, status=review.status.value)
    except DomainError as exc:
        raise HTTPException(422, {"code": exc.code, "message": str(exc)})

@router.get("/reviews/{review_id}", response_model=ReviewView)
async def get_review(review_id: UUID, principal: Principal = Depends(current_principal),
                     service: ReviewService = Depends(get_review_service)):
    try:
        r = await service.get(principal, review_id)
        return ReviewView(review_id=r.id, status=r.status.value, report=r.report, reviewer_comment=r.reviewer_comment)
    except DomainError as exc:
        raise HTTPException(404 if exc.code == "not_found" else 403, str(exc))

@router.post("/reviews/{review_id}/decision", response_model=ReviewView)
async def decide(review_id: UUID, body: ReviewDecision,
                 principal: Principal = Depends(current_principal),
                 service: ReviewService = Depends(get_review_service)):
    try:
        r = await service.decide(principal, review_id, body.decision, body.comment)
        return ReviewView(review_id=r.id, status=r.status.value, report=r.report, reviewer_comment=r.reviewer_comment)
    except DomainError as exc:
        status = 404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 403
        raise HTTPException(status, str(exc))
