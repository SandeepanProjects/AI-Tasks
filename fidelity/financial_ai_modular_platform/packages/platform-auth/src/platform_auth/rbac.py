from platform_core.errors import AuthorizationError
from .models import Principal

class PermissionDenied(AuthorizationError):
    pass

class RBAC:
    """Generic RBAC engine. Applications define their own permissions."""

    def __init__(self, role_permissions: dict[str, set[str]]):
        self.role_permissions = role_permissions

    def authorize(self, principal: Principal, permission: str) -> None:
        granted = set()
        for role in principal.roles:
            granted.update(self.role_permissions.get(role, set()))
        if permission not in granted:
            raise PermissionDenied(
                f"permission={permission!r} denied for roles={sorted(principal.roles)}"
            )
