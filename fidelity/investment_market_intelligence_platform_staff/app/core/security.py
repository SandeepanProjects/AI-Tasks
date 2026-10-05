from dataclasses import dataclass
from enum import StrEnum
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from app.core.config import settings

bearer = HTTPBearer(auto_error=False)

class Role(StrEnum):
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    ADMIN = "admin"

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[Role]

def _verify_local_token(token: str) -> Principal:
    # Replace this adapter with an OIDC/JWKS verifier in production.
    if not settings.jwt_secret.get_secret_value():
        raise HTTPException(503, "Authentication provider is not configured")
    try:
        payload = jwt.decode(
            token, settings.jwt_secret.get_secret_value(), algorithms=["HS256"],
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            options={"require_exp": True, "require_sub": True},
        )
        tenant, sub = payload.get("tenant_id"), payload.get("sub")
        if not tenant or not isinstance(tenant, str): raise ValueError("tenant_id missing")
        roles = frozenset(Role(r) for r in payload.get("roles", []))
        return Principal(sub, tenant, roles)
    except (JWTError, ValueError):
        raise HTTPException(401, "Invalid bearer token")

async def current_principal(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    if creds is None: raise HTTPException(401, "Bearer token required")
    return _verify_local_token(creds.credentials)

def require_role(*allowed: Role):
    async def dependency(principal: Principal = Depends(current_principal)) -> Principal:
        if not principal.roles.intersection(allowed):
            raise HTTPException(403, "Insufficient role")
        return principal
    return dependency
