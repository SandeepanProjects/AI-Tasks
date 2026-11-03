from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

class ReviewScope(BaseModel):
    assets: list[str] = Field(min_length=1, max_length=20)
    lookback_days: int = Field(ge=1, le=3650)

class CreateReviewRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=4000)
    scope: ReviewScope
    purpose: Literal["research","risk_review","education"] = "research"

class ReviewCreated(BaseModel):
    review_id: UUID
    status: str

class ReviewDecision(BaseModel):
    decision: Literal["approve","request_changes","reject"]
    comment: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def require_reason_for_non_approval(self):
        if self.decision in {"request_changes", "reject"} and len(self.comment.strip()) < 5:
            raise ValueError("A reviewer comment of at least five characters is required")
        return self

class ReviewView(BaseModel):
    review_id: UUID
    status: str
    report: dict | None = None
    reviewer_comment: str | None = None

class EvidenceIngestRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    source_name: str = Field(min_length=1, max_length=256)
    source_uri: str = Field(min_length=1, max_length=2048)
    content: str = Field(min_length=1, max_length=100000)
    metadata: dict = Field(default_factory=dict, max_length=30)

class EvidenceIngestResponse(BaseModel):
    chunks_created: int
