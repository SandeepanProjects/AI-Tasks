from fastapi import APIRouter, HTTPException
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# Demo only. Replace with enterprise IdP/user repository.
DEMO_USERS = {
    "demo": {
        "password_hash": hash_password("demo-password"),
        "tenant_id": "tenant-demo",
        "role": "advisor",
    }
}

@router.post("/token", response_model=TokenResponse)
async def token(request: LoginRequest):
    user = DEMO_USERS.get(request.username)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(
            request.username, user["tenant_id"], user["role"]
        )
    )
