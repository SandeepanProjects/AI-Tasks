import pytest
from app.domain.transitions import validate_transition
from app.domain.schemas import ReviewStatus


def test_valid():
    validate_transition(ReviewStatus.QUEUED, ReviewStatus.RUNNING)


def test_terminal_rejects():
    with pytest.raises(ValueError):
        validate_transition(ReviewStatus.APPROVED, ReviewStatus.RUNNING)
