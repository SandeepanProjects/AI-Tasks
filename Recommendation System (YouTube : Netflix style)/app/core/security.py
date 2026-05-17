import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "dev-secret-key")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class SecurityManager:
    """
    Lightweight API Key auth for internal ML services.
    Replace with OAuth/JWT in real production.
    """

    def verify_api_key(self, api_key: str = Security(api_key_header)) -> bool:
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API Key"
            )

        if api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API Key"
            )

        return True