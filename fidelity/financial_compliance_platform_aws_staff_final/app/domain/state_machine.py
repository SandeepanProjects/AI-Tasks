from app.domain.schemas import ReviewStatus

ALLOWED_TRANSITIONS = {
    ReviewStatus.QUEUED: {ReviewStatus.RUNNING, ReviewStatus.FAILED},
    ReviewStatus.RUNNING: {ReviewStatus.NEEDS_HUMAN, ReviewStatus.FAILED},
    ReviewStatus.NEEDS_HUMAN: {ReviewStatus.DECISION_QUEUED, ReviewStatus.FAILED},
    ReviewStatus.DECISION_QUEUED: {ReviewStatus.RESUMING, ReviewStatus.FAILED},
    ReviewStatus.RESUMING: {ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.FAILED},
    ReviewStatus.APPROVED: set(), ReviewStatus.REJECTED: set(), ReviewStatus.FAILED: set(),
}

def assert_transition(current: str | ReviewStatus, target: str | ReviewStatus) -> None:
    old, new = ReviewStatus(current), ReviewStatus(target)
    if new not in ALLOWED_TRANSITIONS[old]:
        raise ValueError(f"Invalid review transition: {old.value} -> {new.value}")
