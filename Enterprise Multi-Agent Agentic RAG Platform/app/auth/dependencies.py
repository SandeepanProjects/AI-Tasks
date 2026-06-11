from fastapi import HTTPException

from app.auth.permissions import (
    PERMISSIONS
)


def authorize(
    role,
    permission
):

    allowed = PERMISSIONS.get(
        role,
        []
    )

    if permission not in allowed:

        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )