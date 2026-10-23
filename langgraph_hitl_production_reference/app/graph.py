import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt

from app.state import WorkflowState

logger = logging.getLogger(__name__)


def prepare_draft(state: WorkflowState) -> dict:
    # Replace with your retrieval and LLM generation.
    # Do not perform external side effects here.
    draft = (
        f"Draft analysis for: {state['question']}\n"
        "This is a demonstration draft. Replace it with grounded, cited output."
    )
    return {"draft": draft}


def human_review(state: WorkflowState) -> dict:
    # IMPORTANT: interrupt() resumes this node from its beginning. Keep this
    # node free of non-idempotent side effects before/after the interrupt.
    approval_id = f"approval:{state['thread_id']}:v1"
    decision = interrupt({
        "kind": "human_approval",
        "approval_id": approval_id,
        "thread_id": state["thread_id"],
        "summary": "Review the proposed AI response before it is released.",
        "draft": state.get("draft", ""),
        "allowed_decisions": ["approve", "reject"],
    })

    # Validate again inside the graph; never trust the client payload blindly.
    if not isinstance(decision, dict):
        raise ValueError("Approval payload must be an object")
    if decision.get("approval_id") != approval_id:
        raise ValueError("Approval ID mismatch")
    action = decision.get("decision")
    if action not in {"approve", "reject"}:
        raise ValueError("Decision must be approve or reject")
    reviewer_id = decision.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ValueError("Missing reviewer identity")

    return {
        "approval_status": action,
        "reviewer_id": reviewer_id,
        "reviewer_comment": str(decision.get("comment", ""))[:4000],
    }


def route_after_review(state: WorkflowState) -> Literal["publish", "reject"]:
    return "publish" if state.get("approval_status") == "approve" else "reject"


def publish(state: WorkflowState) -> dict:
    # Replace with your real delivery operation.
    # Use a stable idempotency key such as thread_id + ":publish:v1" in the
    # destination system or an outbox table. A graph checkpoint alone cannot
    # guarantee exactly-once external side effects.
    return {"final_result": state.get("draft", "")}


def reject(state: WorkflowState) -> dict:
    return {"final_result": "The draft was rejected and was not released."}


def build_graph(checkpointer):
    builder = StateGraph(WorkflowState)
    builder.add_node("prepare_draft", prepare_draft)
    builder.add_node("human_review", human_review)
    builder.add_node("publish", publish)
    builder.add_node("reject", reject)

    builder.add_edge(START, "prepare_draft")
    builder.add_edge("prepare_draft", "human_review")
    builder.add_conditional_edges(
        "human_review",
        route_after_review,
        {"publish": "publish", "reject": "reject"},
    )
    builder.add_edge("publish", END)
    builder.add_edge("reject", END)
    return builder.compile(checkpointer=checkpointer)
