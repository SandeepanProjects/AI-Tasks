from fastapi import HTTPException

from app.enterprise.rbac.permissions import ROLE_PERMISSIONS


class RBACMiddleware:

    @staticmethod
    def check_permission(user, action):

        role = user.get("role")

        allowed = ROLE_PERMISSIONS.get(role, [])

        if action not in allowed:

            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )