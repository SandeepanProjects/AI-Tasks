# app/core/security.py

import os
import re
import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings


# =========================================================
# API KEY SECURITY
# =========================================================

API_KEY_NAME = "x-api-key"

api_key_header = APIKeyHeader(
    name=API_KEY_NAME,
    auto_error=False,
)


def validate_api_key(
    api_key: Optional[str] = Security(api_key_header),
):
    """
    Validates incoming API key.
    """

    expected_api_key = os.getenv("RAG_API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server API key not configured",
        )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if not secrets.compare_digest(
        api_key,
        expected_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key


# =========================================================
# PROMPT INJECTION PROTECTION
# =========================================================

PROMPT_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"reveal system prompt",
    r"bypass security",
    r"act as root",
    r"show hidden instructions",
    r"developer message",
    r"pretend you are",
    r"disable safety",
]


def detect_prompt_injection(text: str) -> bool:
    """
    Detects common prompt injection attempts.
    """

    normalized = text.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, normalized):
            return True

    return False


def validate_user_input(text: str):
    """
    Validates user query before retrieval/generation.
    """

    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty",
        )

    if len(text) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query too large",
        )

    if detect_prompt_injection(text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Potential prompt injection detected",
        )

    return text


# =========================================================
# OUTPUT SANITIZATION
# =========================================================

PII_PATTERNS = [
    r"\\b\\d{3}-\\d{2}-\\d{4}\\b",  # SSN
    r"\\b(?:\\d[ -]*?){13,16}\\b",  # Credit cards
]


def sanitize_output(text: str) -> str:
    """
    Removes potential sensitive information.
    """

    sanitized = text

    for pattern in PII_PATTERNS:
        sanitized = re.sub(
            pattern,
            "[REDACTED]",
            sanitized,
        )

    return sanitized


# =========================================================
# RATE LIMITING PLACEHOLDER
# =========================================================

class RateLimiter:
    """
    Placeholder for Redis-based rate limiting.
    """

    def __init__(self):
        self.max_requests = 100

    def check_rate_limit(
        self,
        user_id: str,
    ) -> bool:
        """
        Replace with Redis sliding window implementation.
        """

        return True


rate_limiter = RateLimiter()

