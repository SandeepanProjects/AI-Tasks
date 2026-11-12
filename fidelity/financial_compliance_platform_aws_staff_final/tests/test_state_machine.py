import pytest
from app.domain.state_machine import assert_transition

def test_valid_review_lifecycle_transitions():
    assert_transition("queued", "running")
    assert_transition("running", "needs_human")
    assert_transition("needs_human", "decision_queued")
    assert_transition("decision_queued", "resuming")
    assert_transition("resuming", "approved")

def test_terminal_state_cannot_be_reopened():
    with pytest.raises(ValueError): assert_transition("approved", "running")

def test_cannot_skip_human_decision_queue():
    with pytest.raises(ValueError): assert_transition("needs_human", "approved")
