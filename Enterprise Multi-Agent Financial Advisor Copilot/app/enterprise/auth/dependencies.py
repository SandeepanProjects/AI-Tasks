# app/auth/dependencies.py

from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import HTTPBearer

from app.auth.jwt import JWTService


security = HTTPBearer()


def get_current_user(
    token=Depends(security)
):

    try:

        return JWTService.verify_token(
            token.credentials
        )

    except Exception:

        raise HTTPException(
            status_code=401,

            detail="Unauthorized"
        )