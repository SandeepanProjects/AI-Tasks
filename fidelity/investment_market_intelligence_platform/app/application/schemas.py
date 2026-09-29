from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from uuid import UUID

class ReviewScope(BaseModel):
    assets: list[str] = Field(min_length=1, max_length=20)
    lookback_days: int = Field(ge=1, le=365)

class CreateReviewRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=4000)
    scope: ReviewScope
    purpose: Literal["research", "risk_review", "education"] = "research"

class ReviewCreated(BaseModel):
    review_id: UUID
    status: str

class ReviewDecision(BaseModel):
    decision: Literal["approve", "request_changes", "reject"]
    comment: str = Field(default="", max_length=2000)

class ReviewView(BaseModel):
    review_id: UUID
    status: str
    report: dict | None = None
    reviewer_comment: str | None = None
