from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ReviewStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    NEEDS_HUMAN = "needs_human"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Evidence(BaseModel):
    policy_id: str
    policy_code: str
    policy_version: str
    quote: str = Field(min_length=1, max_length=2000)


class Finding(BaseModel):
    category: Literal["performance", "risk", "fees", "general"]
    severity: Severity
    statement: str
    rationale: str
    evidence: list[Evidence] = Field(default_factory=list)


class AgentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: str
    tenant_id: str
    statement: str
    policies: list[dict]
    task_id: str


class AgentOutput(BaseModel):
    agent_name: str
    findings: list[Finding] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    statement: str = Field(min_length=5, max_length=20000)


class DecisionRequest(BaseModel):
    decision: Literal["approve", "reject", "request_changes"]
    comment: str = Field(default="", max_length=4000)
