from uuid import UUID
from app.core.errors import NotFoundError, AuthorizationError, ConflictError
from app.core.security import Principal, Role
from app.core.config import settings
from app.domain.models import Review, ReviewStatus
from app.domain.policies import validate_research_request
from app.application.ports import ReviewRepository, ResearchWorkflow

class ReviewService:
    def __init__(self, repo: ReviewRepository, workflow: ResearchWorkflow):
        self.repo, self.workflow = repo, workflow

    async def create(self, principal: Principal, question: str, assets: list[str], lookback_days: int) -> Review:
        validate_research_request(question, assets, lookback_days, settings.max_research_lookback_days)
        review = Review(tenant_id=principal.tenant_id, created_by=principal.subject,
                        question=question, assets=assets, lookback_days=lookback_days)
        await self.repo.add(review)
        # Inline for the reference scaffold. Production: enqueue an idempotent Celery task.
        review.status = ReviewStatus.RUNNING
        await self.repo.save(review)
        try:
            review.report = await self.workflow.run(review)
            review.status = ReviewStatus.AWAITING_REVIEW if settings.review_required else ReviewStatus.APPROVED
        except Exception:
            review.status = ReviewStatus.FAILED
            await self.repo.save(review)
            raise
        await self.repo.save(review)
        return review

    async def get(self, principal: Principal, review_id: UUID) -> Review:
        review = await self.repo.get(principal.tenant_id, review_id)
        if not review:
            raise NotFoundError("Review not found")
        return review

    async def decide(self, principal: Principal, review_id: UUID, decision: str, comment: str) -> Review:
        if Role.REVIEWER not in principal.roles and Role.ADMIN not in principal.roles:
            raise AuthorizationError("Reviewer role required")
        review = await self.get(principal, review_id)
        if review.status != ReviewStatus.AWAITING_REVIEW:
            raise ConflictError("Review is not awaiting a decision")
        review.reviewer_id, review.reviewer_comment = principal.subject, comment
        if decision == "approve":
            review.status = ReviewStatus.APPROVED
        elif decision == "request_changes":
            review.status = ReviewStatus.CHANGES_REQUESTED
        else:
            review.status = ReviewStatus.REJECTED
        await self.repo.save(review)
        return review
