from typing import TypedDict

class CopilotState(TypedDict, total=False):
    tenant_id: str
    user_id: str
    thread_id: str
    question: str
    context: str
    answer: str
    risk_score: float
    requires_human_approval: bool
    guardrail_error: str
    human_decision: dict
