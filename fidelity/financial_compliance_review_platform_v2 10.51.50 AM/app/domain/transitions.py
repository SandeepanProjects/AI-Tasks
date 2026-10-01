from app.domain.schemas import ReviewStatus

ALLOWED = {
    ReviewStatus.QUEUED: {ReviewStatus.RUNNING, ReviewStatus.FAILED},
    ReviewStatus.RUNNING: {ReviewStatus.NEEDS_HUMAN, ReviewStatus.FAILED},
    ReviewStatus.NEEDS_HUMAN: {ReviewStatus.APPROVED, ReviewStatus.REJECTED},
    ReviewStatus.APPROVED: set(),
    ReviewStatus.REJECTED: set(),
    ReviewStatus.FAILED: set(),
}


def validate_transition(old: ReviewStatus, new: ReviewStatus):
    if new not in ALLOWED[old]:
        raise ValueError(f"Invalid transition {old} -> {new}")
