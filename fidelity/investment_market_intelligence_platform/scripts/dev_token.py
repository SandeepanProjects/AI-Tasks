from datetime import datetime, timedelta, timezone
from jose import jwt
import os
secret = os.getenv("JWT_SECRET", "development-only-change-me")
now = datetime.now(timezone.utc)
print(jwt.encode({
    "sub": "analyst-local", "tenant_id": "demo-tenant",
    "roles": ["analyst", "reviewer"], "iss": "investment-platform",
    "aud": "investment-api", "iat": now, "exp": now + timedelta(minutes=30)
}, secret, algorithm="HS256"))
