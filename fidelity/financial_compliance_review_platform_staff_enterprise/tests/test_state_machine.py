import pytest
from app.domain.state_machine import assert_transition

def test_valid_human_transition():
    assert_transition("needs_human", "approved")

def test_terminal_state_cannot_be_reopened():
    with pytest.raises(ValueError):
        assert_transition("approved", "processing")
