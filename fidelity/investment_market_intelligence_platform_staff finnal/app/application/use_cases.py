from uuid import UUID
from app.application.ports import ReviewRepository
from app.core.config import settings
from app.core.errors import AuthorizationError, ConflictError, NotFoundError
from app.core.security import Principal, Role
from app.domain.models import Review, ReviewStatus
from app.domain.policies import validate_research_request

class ReviewService:
    def __init__(self, repo: ReviewRepository):
        self.repo = repo

    async def create(self, principal: Principal, question: str, assets: list[str], lookback_days: int,
                     purpose: str, idempotency_key: str) -> Review:
        validate_research_request(question, assets, lookback_days, settings.max_research_lookback_days)
        review = Review(principal.tenant_id, principal.subject, question, assets, lookback_days, purpose=purpose)
        created, existing = await self.repo.add(review, idempotency_key)
        if not created:
            if existing is not None:
                return existing
            raise ConflictError("Idempotency key already used")
        return review

    async def get(self, principal: Principal, review_id: UUID) -> Review:
        review = await self.repo.get(principal.tenant_id, review_id)
        if not review: raise NotFoundError("Review not found")
        return review

    async def decide(self, principal: Principal, review_id: UUID, decision: str, comment: str) -> Review:
        if not principal.roles.intersection({Role.REVIEWER, Role.ADMIN}):
            raise AuthorizationError("Reviewer role required")
        review = await self.get(principal, review_id)
        if review.status != ReviewStatus.AWAITING_REVIEW:
            raise ConflictError("Review is not awaiting a decision")
        target = {"approve": ReviewStatus.APPROVED, "request_changes": ReviewStatus.CHANGES_REQUESTED,
                  "reject": ReviewStatus.REJECTED}[decision]
        review.reviewer_id, review.reviewer_comment = principal.subject, comment
        review.transition(target)
        await self.repo.save_with_audit(review, expected_version=review.version - 1,
            actor_id=principal.subject, action=f"review.{decision}", details={"comment": comment})
        return review
    async def retry_failed(self, principal: Principal, review_id: UUID) -> Review:
        if Role.ADMIN not in principal.roles:
            raise AuthorizationError("Administrator role required to retry failed reviews")
        review = await self.get(principal, review_id)
        if review.status != ReviewStatus.FAILED:
            raise ConflictError("Only failed reviews can be retried")
        expected_version = review.version
        review.transition(ReviewStatus.QUEUED)
        review.report = None
        review.reviewer_id = None
        review.reviewer_comment = None
        await self.repo.requeue_failed(review, expected_version, principal.subject)
        return review

