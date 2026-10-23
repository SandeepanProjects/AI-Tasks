from typing import TypedDict, NotRequired

class WorkflowState(TypedDict):
    request_id: str
    tenant_id: str
    question: str
    retrieved_context: NotRequired[str]
    analysis: NotRequired[str]
    compliance_result: NotRequired[str]
    final_answer: NotRequired[str]
