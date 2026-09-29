from app.security.rbac import permissions_for, Permission

def test_analyst_cannot_approve():
    assert Permission.REVIEW_APPROVE not in permissions_for(frozenset({"analyst"}))

def test_reviewer_can_approve():
    assert Permission.REVIEW_APPROVE in permissions_for(frozenset({"reviewer"}))
