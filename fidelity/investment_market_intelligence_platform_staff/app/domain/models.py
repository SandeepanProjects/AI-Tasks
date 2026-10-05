from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4
from app.core.errors import ConflictError

class ReviewStatus(StrEnum):
    QUEUED="queued"; RUNNING="running"; AWAITING_REVIEW="awaiting_review"
    APPROVED="approved"; CHANGES_REQUESTED="changes_requested"; REJECTED="rejected"; FAILED="failed"

_ALLOWED = {
    ReviewStatus.QUEUED: {ReviewStatus.RUNNING, ReviewStatus.FAILED},
    ReviewStatus.RUNNING: {ReviewStatus.AWAITING_REVIEW, ReviewStatus.FAILED},
    ReviewStatus.AWAITING_REVIEW: {ReviewStatus.APPROVED, ReviewStatus.CHANGES_REQUESTED, ReviewStatus.REJECTED},
    ReviewStatus.CHANGES_REQUESTED: {ReviewStatus.QUEUED, ReviewStatus.REJECTED},
    ReviewStatus.APPROVED: set(), ReviewStatus.REJECTED: set(), ReviewStatus.FAILED: {ReviewStatus.QUEUED},
}

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
    purpose: str = "research"
    id: UUID = field(default_factory=uuid4)
    status: ReviewStatus = ReviewStatus.QUEUED
    report: dict[str, Any] | None = None
    reviewer_id: str | None = None
    reviewer_comment: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1

    def transition(self, target: ReviewStatus) -> None:
        if target not in _ALLOWED[self.status]:
            raise ConflictError(f"Illegal review transition: {self.status} -> {target}")
        self.status = target
        self.version += 1
