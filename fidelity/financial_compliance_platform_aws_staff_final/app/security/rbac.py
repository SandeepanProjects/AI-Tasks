from enum import StrEnum
from fastapi import Depends, HTTPException
from app.auth import Principal, current_principal

class Permission(StrEnum):
    REVIEW_CREATE = "review:create"
    REVIEW_READ = "review:read"
    REVIEW_APPROVE = "review:approve"
    POLICY_INGEST = "policy:ingest"
    AUDIT_READ = "audit:read"

# Role mapping is deterministic policy. Production may source assignments from an IdP/OPA.
ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "analyst": frozenset({Permission.REVIEW_CREATE, Permission.REVIEW_READ}),
    "reviewer": frozenset({Permission.REVIEW_READ, Permission.REVIEW_APPROVE}),
    "compliance_admin": frozenset(Permission),
    "policy_admin": frozenset({Permission.POLICY_INGEST, Permission.REVIEW_READ}),
    "auditor": frozenset({Permission.REVIEW_READ, Permission.AUDIT_READ}),
}

def permissions_for(roles: frozenset[str]) -> frozenset[Permission]:
    return frozenset(p for role in roles for p in ROLE_PERMISSIONS.get(role, frozenset()))

def require_permission(permission: Permission):
    def dependency(principal: Principal = Depends(current_principal)) -> Principal:
        if permission not in permissions_for(principal.roles):
            raise HTTPException(status_code=403, detail="Insufficient permission")
        return principal
    return dependency
