from dataclasses import dataclass
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.security import decode_token

bearer = HTTPBearer()

@dataclass(frozen=True)
class Principal:
    user_id: str
    tenant_id: str
    role: str

def get_current_principal(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> Principal:
    payload = decode_token(credentials.credentials)
    return Principal(
        user_id=payload["sub"],
        tenant_id=payload["tenant_id"],
        role=payload["role"],
    )

def require_roles(*roles: str):
    def dependency(principal: Principal = Depends(get_current_principal)):
        if principal.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal
    return dependency
