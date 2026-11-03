import pytest
from app.domain.models import Review, ReviewStatus
from app.core.errors import ConflictError

def test_review_transition():
    r=Review("t","u","q",["BTC"],7)
    r.transition(ReviewStatus.RUNNING)
    assert r.status==ReviewStatus.RUNNING
    r.transition(ReviewStatus.AWAITING_REVIEW)
    r.transition(ReviewStatus.APPROVED)
    with pytest.raises(ConflictError): r.transition(ReviewStatus.REJECTED)

def test_illegal_transition():
    r=Review("t","u","q",["BTC"],7)
    with pytest.raises(ConflictError): r.transition(ReviewStatus.APPROVED)
