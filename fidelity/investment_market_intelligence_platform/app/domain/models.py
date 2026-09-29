from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

class ReviewStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"
    FAILED = "failed"

@dataclass
class Evidence:
    evidence_id: str
    source_name: str
    source_uri: str
    observed_at: datetime
    content: str
    content_hash: str
    tenant_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Review:
    tenant_id: str
    created_by: str
    question: str
    assets: list[str]
    lookback_days: int
    id: UUID = field(default_factory=uuid4)
    status: ReviewStatus = ReviewStatus.QUEUED
    report: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reviewer_id: str | None = None
    reviewer_comment: str | None = None
