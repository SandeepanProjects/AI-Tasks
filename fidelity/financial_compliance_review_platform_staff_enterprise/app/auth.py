from dataclasses import dataclass
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    sub: str
    tenant_id: str
    roles: frozenset[str]


def current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    if not credentials:
        raise HTTPException(401, "Bearer token required")
    try:
        c = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "exp", "iss", "aud", "tenant_id"]},
        )
        return Principal(
            str(c["sub"]), str(c["tenant_id"]), frozenset(c.get("roles", []))
        )
    except Exception:
        raise HTTPException(401, "Invalid bearer token")


def require_role(role: str):
    def dep(p: Principal = Depends(current_principal)):
        if role not in p.roles:
            raise HTTPException(403, "Insufficient role")
        return p

    return dep
