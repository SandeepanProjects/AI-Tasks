import pytest
from app.domain.schemas import ReviewStatus as S
from app.domain.transitions import validate_transition


def test_valid_transition():
    validate_transition(S.QUEUED, S.RUNNING)


def test_terminal_cannot_transition():
    with pytest.raises(ValueError):
        validate_transition(S.APPROVED, S.RUNNING)
