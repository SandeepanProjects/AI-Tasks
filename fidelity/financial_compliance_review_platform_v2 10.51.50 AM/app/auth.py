from dataclasses import dataclass
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient, decode
from app.config import settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str]


async def current_user(c: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if settings.auth_mode == "dev":
        if not c or c.credentials != "local-dev-token":
            raise HTTPException(401, "Invalid dev token")
        return Principal(
            "local-user", "demo-tenant", frozenset({"reviewer", "approver", "admin"})
        )
    if settings.auth_mode != "jwt" or not all(
        (settings.jwt_issuer, settings.jwt_audience, settings.jwt_jwks_url)
    ):
        raise HTTPException(503, "JWT not configured")
    if not c:
        raise HTTPException(401, "Bearer token required")
    try:
        key = (
            PyJWKClient(settings.jwt_jwks_url)
            .get_signing_key_from_jwt(c.credentials)
            .key
        )
        claims = decode(
            c.credentials,
            key,
            algorithms=["RS256", "ES256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
        if not claims.get("tenant_id") or not isinstance(claims.get("roles"), list):
            raise ValueError()
        return Principal(claims["sub"], claims["tenant_id"], frozenset(claims["roles"]))
    except Exception as e:
        raise HTTPException(401, "Invalid access token") from e


def require(*roles):
    async def dep(p: Principal = Depends(current_user)):
        if not p.roles.intersection(roles):
            raise HTTPException(403, "Forbidden")
        return p

    return dep
