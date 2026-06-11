from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from app.enterprise.auth.jwt import JWTService


security = HTTPBearer()


def get_current_user(token=Depends(security)):

    try:

        payload = JWTService.decode_token(
            token.credentials
        )

        return payload

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )