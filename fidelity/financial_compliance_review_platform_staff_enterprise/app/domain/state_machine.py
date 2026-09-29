from enum import StrEnum

class ReviewStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    NEEDS_HUMAN = "needs_human"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"

_ALLOWED = {
    ReviewStatus.RECEIVED: {ReviewStatus.PROCESSING, ReviewStatus.FAILED},
    ReviewStatus.PROCESSING: {ReviewStatus.NEEDS_HUMAN, ReviewStatus.FAILED},
    ReviewStatus.NEEDS_HUMAN: {ReviewStatus.APPROVED, ReviewStatus.REJECTED},
    ReviewStatus.APPROVED: set(),
    ReviewStatus.REJECTED: set(),
    ReviewStatus.FAILED: set(),
}

def assert_transition(current: str, target: str) -> None:
    if target not in {s.value for s in _ALLOWED.get(ReviewStatus(current), set())}:
        raise ValueError(f"Invalid review transition: {current} -> {target}")
