from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from uuid import uuid4, UUID

from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field
from langgraph.types import Command

from app.db import (
    create_database_resources, register_workflow, verify_ownership,
    get_approval_audit, record_approval,
)
from app.graph import build_graph

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

pool = None
checkpointer = None
graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool, checkpointer, graph
    pool, checkpointer = create_database_resources()
    graph = build_graph(checkpointer)
    yield
    if pool is not None:
        pool.close()


app = FastAPI(title="Durable LangGraph HITL", lifespan=lifespan)


class StartRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)


class ApprovalRequest(BaseModel):
    approval_id: str = Field(min_length=1, max_length=200)
    decision: str
    comment: str | None = Field(default=None, max_length=4000)


def authenticated_principal(
    x_tenant_id: str | None = Header(default=None),
    x_reviewer_id: str | None = Header(default=None),
):
    # DEMO ONLY. Replace with verified JWT/OIDC authentication and authorization.
    # Never treat caller-supplied headers as identity in production.
    if not x_tenant_id or not x_reviewer_id:
        raise HTTPException(status_code=401, detail="Authenticated tenant and reviewer required")
    return {"tenant_id": x_tenant_id, "reviewer_id": x_reviewer_id}


def require_thread_access(thread_id: str, principal: dict):
    try:
        UUID(thread_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid thread ID")
    if not verify_ownership(pool, thread_id, principal["tenant_id"]):
        # Avoid disclosing whether another tenant owns the workflow.
        raise HTTPException(status_code=404, detail="Workflow not found")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/workflows")
def start_workflow(
    body: StartRequest,
    principal: dict = Depends(authenticated_principal),
):
    thread_id = str(uuid4())
    request_id = str(uuid4())
    register_workflow(pool, thread_id, principal["tenant_id"])
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 25,
    }
    state = {
        "thread_id": thread_id,
        "tenant_id": principal["tenant_id"],
        "request_id": request_id,
        "question": body.question,
    }
    try:
        result = graph.invoke(state, config=config)
    except Exception:
        logger.exception("Workflow execution failed thread_id=%s", thread_id)
        # Checkpoint may exist even when the request failed. Caller can inspect
        # state and recover by using the same thread ID.
        return {
            "thread_id": thread_id,
            "status": "failed_recoverable",
            "message": "Execution failed; inspect state and retry/resume this thread.",
        }

    if result.get("__interrupt__"):
        return {
            "thread_id": thread_id,
            "status": "awaiting_approval",
            "interrupts": [
                {"value": item.value, "id": item.id}
                for item in result["__interrupt__"]
            ],
        }
    return {"thread_id": thread_id, "status": "completed", "result": result.get("final_result")}


@app.get("/workflows/{thread_id}")
def get_workflow(thread_id: str, principal: dict = Depends(authenticated_principal)):
    require_thread_access(thread_id, principal)
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Workflow state not found")

    interrupts = []
    for item in getattr(snapshot, "tasks", ()):
        for intr in getattr(item, "interrupts", ()):
            interrupts.append({"id": intr.id, "value": intr.value})

    return {
        "thread_id": thread_id,
        "status": "awaiting_approval" if snapshot.next and interrupts else (
            "in_progress" if snapshot.next else "completed"
        ),
        "values": snapshot.values,
        "next": list(snapshot.next),
        "interrupts": interrupts,
        "checkpoint_id": snapshot.config.get("configurable", {}).get("checkpoint_id"),
    }


@app.post("/workflows/{thread_id}/approve")
def approve_workflow(
    thread_id: str,
    body: ApprovalRequest,
    principal: dict = Depends(authenticated_principal),
):
    require_thread_access(thread_id, principal)
    if body.decision not in {"approve", "reject"}:
        raise HTTPException(status_code=422, detail="decision must be 'approve' or 'reject'")

    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}
    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Workflow state not found")

    # If client retries the same request after a network failure, return the
    # persisted decision status rather than accepting a conflicting decision.
    existing = get_approval_audit(pool, thread_id, body.approval_id)
    if existing:
        if existing["decision"] != body.decision:
            raise HTTPException(status_code=409, detail="Conflicting decision for this approval ID")
        return {
            "thread_id": thread_id,
            "status": "decision_already_recorded",
            "decision": existing["decision"],
        }

    if not snapshot.next:
        raise HTTPException(status_code=409, detail="Workflow is not waiting for approval")

    # Ensure the requested approval ID matches the currently pending interrupt.
    pending = []
    for task in getattr(snapshot, "tasks", ()):
        for intr in getattr(task, "interrupts", ()):
            if isinstance(intr.value, dict):
                pending.append(intr.value.get("approval_id"))
    if body.approval_id not in pending:
        raise HTTPException(status_code=409, detail="Approval ID is not currently pending")

    # In real deployments, reviewer role/entitlement and segregation-of-duties
    # policies must be checked before recording or resuming.
    inserted = record_approval(
        pool,
        thread_id=thread_id,
        tenant_id=principal["tenant_id"],
        approval_id=body.approval_id,
        reviewer_id=principal["reviewer_id"],
        decision=body.decision,
        comment=body.comment,
    )
    if not inserted:
        existing = get_approval_audit(pool, thread_id, body.approval_id)
        if existing and existing["decision"] != body.decision:
            raise HTTPException(status_code=409, detail="Conflicting decision for this approval ID")

    resume_value = {
        "approval_id": body.approval_id,
        "decision": body.decision,
        "reviewer_id": principal["reviewer_id"],
        "comment": body.comment or "",
    }
    try:
        result = graph.invoke(Command(resume=resume_value), config=config)
    except Exception:
        logger.exception("Resume failed thread_id=%s approval_id=%s", thread_id, body.approval_id)
        # Decision audit and graph checkpoint are durable. Retry recovery using
        # the same thread after inspecting its current state. For high assurance,
        # use a transactional outbox/worker to reconcile audit-vs-graph status.
        raise HTTPException(
            status_code=503,
            detail="Decision recorded, but workflow resume failed; retry recovery for this thread",
        )

    if result.get("__interrupt__"):
        return {
            "thread_id": thread_id,
            "status": "awaiting_approval",
            "interrupts": [
                {"value": item.value, "id": item.id}
                for item in result["__interrupt__"]
            ],
        }
    return {
        "thread_id": thread_id,
        "status": "completed",
        "decision": body.decision,
        "result": result.get("final_result"),
    }


@app.post("/workflows/{thread_id}/recover")
def recover_workflow(thread_id: str, principal: dict = Depends(authenticated_principal)):
    require_thread_access(thread_id, principal)
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}
    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Workflow state not found")
    if not snapshot.next:
        return {"thread_id": thread_id, "status": "completed", "result": snapshot.values.get("final_result")}

    # This endpoint is for recovery of pending graph execution, not to supply
    # a human decision. If an interrupt is pending, the reviewer must use
    # /approve; invoking None does not approve it.
    if any(getattr(task, "interrupts", ()) for task in getattr(snapshot, "tasks", ())):
        return {"thread_id": thread_id, "status": "awaiting_approval", "message": "Submit the recorded approval decision."}

    try:
        result = graph.invoke(None, config=config)
    except Exception:
        logger.exception("Recovery failed thread_id=%s", thread_id)
        raise HTTPException(status_code=503, detail="Recovery failed; checkpoint retained")
    if result.get("__interrupt__"):
        return {
            "thread_id": thread_id,
            "status": "awaiting_approval",
            "interrupts": [
                {"value": item.value, "id": item.id}
                for item in result["__interrupt__"]
            ],
        }
    return {"thread_id": thread_id, "status": "completed", "result": result.get("final_result")}
