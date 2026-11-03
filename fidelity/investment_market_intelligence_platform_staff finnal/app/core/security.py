from dataclasses import dataclass
from enum import StrEnum
import time
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt, jwk
from jose.exceptions import JWKError
import httpx
from app.core.config import settings

bearer = HTTPBearer(auto_error=False)
_jwks_cache: dict | None = None
_jwks_expiry = 0.0

class Role(StrEnum):
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    ADMIN = "admin"

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str]


def _principal_from_claims(payload: dict) -> Principal:
    tenant, subject = payload.get("tenant_id"), payload.get("sub")
    roles = payload.get("roles", [])
    if (not isinstance(tenant, str) or not tenant or len(tenant) > 128 or
            not isinstance(subject, str) or not subject or len(subject) > 256):
        raise ValueError("Required tenant_id/sub claim missing or exceeds allowed length")
    if not isinstance(roles, list) or any(not isinstance(role, str) for role in roles):
        raise ValueError("roles claim must be a list of strings")
    allowed = {Role.ANALYST, Role.REVIEWER, Role.ADMIN}
    if not set(roles).issubset(allowed):
        raise ValueError("Unknown role in token")
    return Principal(subject, tenant, frozenset(roles))


def _verify_local_token(token: str) -> Principal:
    if not settings.jwt_secret.get_secret_value():
        raise HTTPException(503, "Local JWT authentication is not configured")
    try:
        claims = jwt.decode(token, settings.jwt_secret.get_secret_value(), algorithms=["HS256"],
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            options={"require_exp": True, "require_sub": True})
        return _principal_from_claims(claims)
    except (JWTError, ValueError):
        raise HTTPException(401, "Invalid bearer token")


async def _load_jwks(force: bool = False) -> dict:
    global _jwks_cache, _jwks_expiry
    if not force and _jwks_cache and time.monotonic() < _jwks_expiry:
        return _jwks_cache
    if not settings.oidc_jwks_url:
        raise HTTPException(503, "OIDC JWKS URL is not configured")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.oidc_jwks_url)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
                raise HTTPException(503, "OIDC JWKS response has an invalid shape")
            _jwks_cache = payload
            _jwks_expiry = time.monotonic() + 300
            return _jwks_cache
    except httpx.HTTPError as exc:
        raise HTTPException(503, "OIDC key service unavailable") from exc


async def _verify_oidc_token(token: str) -> Principal:
    try:
        header = jwt.get_unverified_header(token)
        keys = await _load_jwks()
        key_data = next((key for key in keys.get("keys", []) if key.get("kid") == header.get("kid")), None)
        if not key_data:
            # Key rotation may have occurred while the cache was still warm.
            keys = await _load_jwks(force=True)
            key_data = next((key for key in keys.get("keys", []) if key.get("kid") == header.get("kid")), None)
        if not key_data:
            raise ValueError("Signing key not found")
        public_key = jwk.construct(key_data)
        claims = jwt.decode(token, public_key, algorithms=["RS256"], issuer=settings.jwt_issuer,
            audience=settings.jwt_audience, options={"require_exp": True, "require_sub": True})
        return _principal_from_claims(claims)
    except HTTPException:
        raise
    except (JWTError, JWKError, ValueError, StopIteration):
        raise HTTPException(401, "Invalid bearer token")


async def current_principal(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Principal:
    if creds is None:
        raise HTTPException(401, "Bearer token required")
    if settings.auth_mode == "oidc":
        return await _verify_oidc_token(creds.credentials)
    if settings.app_env.lower() in {"production", "prod"}:
        raise HTTPException(503, "Local JWT is disabled in production")
    return _verify_local_token(creds.credentials)


def require_role(*allowed: str):
    async def dependency(principal: Principal = Depends(current_principal)) -> Principal:
        if not principal.roles.intersection(allowed):
            raise HTTPException(403, "Insufficient role")
        return principal
    return dependency
