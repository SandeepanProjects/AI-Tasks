from pydantic import BaseModel, Field
from typing import Literal

class ReviewDecisionCommand(BaseModel):
    decision: Literal["approve", "reject"]
    rationale: str = Field(min_length=10, max_length=2000)
    assessment_version: str = Field(min_length=1, max_length=64)
