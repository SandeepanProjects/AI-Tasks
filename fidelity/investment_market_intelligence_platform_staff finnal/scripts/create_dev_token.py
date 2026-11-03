"""Create a short-lived local HS256 token for development only."""
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

secret = settings.jwt_secret.get_secret_value()
if len(secret) < 32:
    raise SystemExit("Set JWT_SECRET to a random value of at least 32 characters in .env")
now = datetime.now(timezone.utc)
payload = {
    "sub": os.getenv("DEV_SUBJECT", "local-analyst"),
    "tenant_id": os.getenv("DEV_TENANT_ID", "demo-tenant"),
    "roles": os.getenv("DEV_ROLES", "analyst,reviewer,admin").split(","),
    "iss": settings.jwt_issuer,
    "aud": settings.jwt_audience,
    "iat": now,
    "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
}
print(jwt.encode(payload, secret, algorithm="HS256"))
