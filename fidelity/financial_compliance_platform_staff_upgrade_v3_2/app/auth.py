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
        subject, tenant_id, roles = c.get("sub"), c.get("tenant_id"), c.get("roles", [])
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Invalid subject")
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("Invalid tenant")
        if not isinstance(roles, list) or any(not isinstance(role, str) for role in roles):
            raise ValueError("Invalid roles claim")
        return Principal(subject, tenant_id, frozenset(roles))
    except Exception:
        raise HTTPException(401, "Invalid bearer token")

