from app.domain.schemas import ReviewStatus

ALLOWED = {
    ReviewStatus.QUEUED: {ReviewStatus.RUNNING, ReviewStatus.FAILED},
    ReviewStatus.RUNNING: {ReviewStatus.NEEDS_HUMAN, ReviewStatus.FAILED},
    ReviewStatus.NEEDS_HUMAN: {ReviewStatus.DECISION_QUEUED, ReviewStatus.FAILED},
    ReviewStatus.DECISION_QUEUED: {
        ReviewStatus.APPROVED,
        ReviewStatus.REJECTED,
        ReviewStatus.FAILED,
    },
    ReviewStatus.APPROVED: set(),
    ReviewStatus.REJECTED: set(),
    ReviewStatus.FAILED: set(),
}


def validate_transition(old, new):
    if new not in ALLOWED[old]:
        raise ValueError(f"Invalid transition {old} -> {new}")
