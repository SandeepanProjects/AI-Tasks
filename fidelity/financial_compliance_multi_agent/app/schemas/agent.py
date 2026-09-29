from typing import Any
from pydantic import BaseModel, Field
class Claim(BaseModel): text: str; claim_type: str="other"
class Finding(BaseModel):
    claim: str; status: str; rationale: str
    policy_ids: list[int]=Field(default_factory=list)
    policy_codes: list[str]=Field(default_factory=list)
    risk: str="medium"
class ReviewResult(BaseModel):
    summary: str; claims: list[Claim]; findings: list[Finding]
    overall_risk: str; recommended_action: str
    citations_validated: bool=False
    metadata: dict[str,Any]=Field(default_factory=dict)
