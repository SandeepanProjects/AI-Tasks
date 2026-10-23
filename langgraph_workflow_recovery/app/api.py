import logging
import os
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from langgraph.errors import GraphRecursionError

from app.graph import build_graph, make_checkpointer

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ["DATABASE_URL"]

pool = None
checkpointer = None
graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool, checkpointer, graph
    pool, checkpointer = make_checkpointer(DATABASE_URL)
    graph = build_graph(checkpointer)
    yield
    if pool is not None:
        pool.close()


app = FastAPI(title="LangGraph Durable Workflow Recovery", lifespan=lifespan)


class StartRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10_000)


class StartResponse(BaseModel):
    thread_id: str
    status: str
    result: dict | None = None


class ResumeRequest(BaseModel):
    # Optional input to update state before continuing is deliberately omitted
    # here. For normal crash recovery, resume with the saved state, not a new
    # client-supplied replacement state.
    pass


def _authorize_thread(thread_id: str, x_tenant_id: str | None) -> None:
    # DEMO AUTHORIZATION PLACEHOLDER:
    # In production, derive tenant/user from a verified JWT or service identity,
    # and persist an ownership mapping (thread_id -> tenant_id) in your app DB.
    # Never trust a client-provided tenant header as authentication.
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing authenticated tenant context")
    try:
        UUID(thread_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid thread_id")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/workflows", response_model=StartResponse)
def start_workflow(
    body: StartRequest,
    x_tenant_id: str | None = Header(default=None),
):
    if graph is None:
        raise HTTPException(status_code=503, detail="Workflow graph not initialized")
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing authenticated tenant context")

    # This tenant value is only safe after replacing the placeholder header
    # with verified auth middleware/dependency.
    thread_id = str(uuid4())
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 25,
    }
    initial_state = {
        "request_id": str(uuid4()),
        "tenant_id": x_tenant_id,
        "question": body.question,
    }

    try:
        result = graph.invoke(initial_state, config=config)
        status = "completed" if result.get("final_answer") else "incomplete"
        return StartResponse(thread_id=thread_id, status=status, result=result)
    except Exception:
        # Checkpoints written before the failure remain in PostgreSQL.
        # Do not return raw exception details to the client.
        logger.exception("Workflow failed thread_id=%s", thread_id)
        return StartResponse(thread_id=thread_id, status="failed_recoverable", result=None)


@app.post("/workflows/{thread_id}/resume", response_model=StartResponse)
def resume_workflow(
    thread_id: str,
    x_tenant_id: str | None = Header(default=None),
):
    if graph is None:
        raise HTTPException(status_code=503, detail="Workflow graph not initialized")
    _authorize_thread(thread_id, x_tenant_id)

    # IMPORTANT: Check ownership in your application database before this call.
    # The same thread_id loads the persisted state. None means continue pending
    # execution from the latest checkpoint; it does not create a new workflow.
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 25,
    }

    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="No saved workflow state for this thread")

    if not snapshot.next:
        return StartResponse(
            thread_id=thread_id,
            status="already_completed",
            result=snapshot.values,
        )

    try:
        result = graph.invoke(None, config=config)
        status = "completed" if result.get("final_answer") else "incomplete"
        return StartResponse(thread_id=thread_id, status=status, result=result)
    except GraphRecursionError:
        logger.exception("Recursion limit reached thread_id=%s", thread_id)
        raise HTTPException(status_code=409, detail="Workflow stopped at its step limit; inspect state")
    except Exception:
        logger.exception("Workflow recovery failed thread_id=%s", thread_id)
        raise HTTPException(status_code=503, detail="Workflow still failing; saved checkpoint retained")


@app.get("/workflows/{thread_id}/state")
def workflow_state(
    thread_id: str,
    x_tenant_id: str | None = Header(default=None),
):
    if graph is None:
        raise HTTPException(status_code=503, detail="Workflow graph not initialized")
    _authorize_thread(thread_id, x_tenant_id)
    # Add a DB-backed ownership check here before reading the checkpoint.
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="No saved workflow state for this thread")

    return {
        "thread_id": thread_id,
        "values": snapshot.values,
        "next": list(snapshot.next),
        "checkpoint_id": snapshot.config.get("configurable", {}).get("checkpoint_id"),
        "metadata": snapshot.metadata,
    }


@app.get("/workflows/{thread_id}/history")
def workflow_history(
    thread_id: str,
    x_tenant_id: str | None = Header(default=None),
    limit: int = 20,
):
    if graph is None:
        raise HTTPException(status_code=503, detail="Workflow graph not initialized")
    _authorize_thread(thread_id, x_tenant_id)
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    config = {"configurable": {"thread_id": thread_id}}
    history = []
    for snapshot in graph.get_state_history(config, limit=limit):
        history.append({
            "checkpoint_id": snapshot.config.get("configurable", {}).get("checkpoint_id"),
            "values": snapshot.values,
            "next": list(snapshot.next),
            "metadata": snapshot.metadata,
            "created_at": snapshot.created_at,
        })
    return {"thread_id": thread_id, "history": history}
