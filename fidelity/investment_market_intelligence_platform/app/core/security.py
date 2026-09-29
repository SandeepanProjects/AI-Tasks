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

async def current_principal(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Principal:
    # Demo verifier. In production, validate OIDC/JWKS, issuer, audience, exp, nbf,
    # key rotation, and token revocation policy.
    if creds is None:
        raise HTTPException(401, "Bearer token required")
    try:
        payload = jwt.decode(
            creds.credentials, settings.jwt_secret, algorithms=["HS256"],
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
        )
        roles = frozenset(Role(r) for r in payload.get("roles", []))
        tenant = payload.get("tenant_id")
        sub = payload.get("sub")
        if not tenant or not sub:
            raise ValueError("missing claims")
        return Principal(subject=sub, tenant_id=tenant, roles=roles)
    except (JWTError, ValueError):
        raise HTTPException(401, "Invalid token")

def require_role(*allowed: Role):
    async def dependency(principal: Principal = Depends(current_principal)) -> Principal:
        if not principal.roles.intersection(allowed):
            raise HTTPException(403, "Insufficient role")
        return principal
    return dependency
