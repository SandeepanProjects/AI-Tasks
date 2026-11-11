from app.domain.state_machine import assert_transition

def validate_transition(old, new):
    assert_transition(old, new)
