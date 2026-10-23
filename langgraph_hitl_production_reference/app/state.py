from typing import NotRequired, TypedDict


class WorkflowState(TypedDict):
    thread_id: str
    tenant_id: str
    request_id: str
    question: str
    draft: NotRequired[str]
    approval_status: NotRequired[str]
    reviewer_id: NotRequired[str]
    reviewer_comment: NotRequired[str]
    final_result: NotRequired[str]
