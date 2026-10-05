from uuid import UUID
from app.application.ports import ReviewRepository, ResearchWorkflow, AuditRepository
from app.core.config import settings
from app.core.errors import AuthorizationError, ConflictError, NotFoundError
from app.core.security import Principal, Role
from app.domain.models import Review, ReviewStatus
from app.domain.policies import validate_research_request

class ReviewService:
    def __init__(self, repo: ReviewRepository, workflow: ResearchWorkflow, audit: AuditRepository):
        self.repo, self.workflow, self.audit = repo, workflow, audit

    async def create(self, principal: Principal, question: str, assets: list[str], lookback_days: int,
                     purpose: str, idempotency_key: str) -> Review:
        validate_research_request(question, assets, lookback_days, settings.max_research_lookback_days)
        review = Review(principal.tenant_id, principal.subject, question, assets, lookback_days, purpose=purpose)
        created = await self.repo.add(review, idempotency_key)
        if not created:
            raise ConflictError("Idempotency key already used")
        await self.audit.append(principal.tenant_id, principal.subject, "review.created", str(review.id),
                                {"purpose": purpose})
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
        await self.repo.save(review, expected_version=review.version - 1)
        await self.audit.append(principal.tenant_id, principal.subject, f"review.{decision}",
                                str(review.id), {"comment": comment})
        return review
