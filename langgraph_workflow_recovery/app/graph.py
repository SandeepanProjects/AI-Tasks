import logging
from typing import Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.state import WorkflowState

logger = logging.getLogger(__name__)


def retrieve_context(state: WorkflowState) -> dict[str, Any]:
    # Replace with tenant-scoped retrieval from your vector database.
    # Do not trust tenant_id from an untrusted request body; set it from
    # authenticated identity in the API layer.
    logger.info("retrieve_context request_id=%s", state["request_id"])
    return {"retrieved_context": f"Example context relevant to: {state['question']}"}


def analyze(state: WorkflowState) -> dict[str, Any]:
    # Replace with an LLM call. Keep the node deterministic where possible,
    # set provider timeouts, and use bounded retries for transient failures.
    logger.info("analyze request_id=%s", state["request_id"])
    return {
        "analysis": (
            f"Analysis based on context: {state.get('retrieved_context', '')}. "
            f"Question: {state['question']}"
        )
    }


def compliance_check(state: WorkflowState) -> dict[str, Any]:
    # Replace with policy retrieval + model/rule-based checks.
    logger.info("compliance_check request_id=%s", state["request_id"])
    analysis = state.get("analysis", "")
    result = "passed" if analysis else "blocked: missing analysis"
    return {"compliance_result": result}


def finalize(state: WorkflowState) -> dict[str, Any]:
    logger.info("finalize request_id=%s", state["request_id"])
    if state.get("compliance_result") != "passed":
        answer = "I cannot provide a response because the compliance check did not pass."
    else:
        answer = f"Draft response: {state.get('analysis', '')}"
    return {"final_answer": answer}


def build_graph(checkpointer: PostgresSaver):
    builder = StateGraph(WorkflowState)
    builder.add_node("retrieve_context", retrieve_context)
    builder.add_node("analyze", analyze)
    builder.add_node("compliance_check", compliance_check)
    builder.add_node("finalize", finalize)

    builder.add_edge(START, "retrieve_context")
    builder.add_edge("retrieve_context", "analyze")
    builder.add_edge("analyze", "compliance_check")
    builder.add_edge("compliance_check", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=checkpointer)


def make_checkpointer(database_url: str) -> tuple[ConnectionPool, PostgresSaver]:
    # autocommit and dict_row are recommended for the Postgres checkpointer.
    pool = ConnectionPool(
        conninfo=database_url,
        min_size=1,
        max_size=10,
        timeout=10,
        max_idle=300,
        kwargs={"autocommit": True, "row_factory": dict_row},
        open=False,
    )
    pool.open(wait=True)
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()  # Run migrations / create checkpoint tables.
    return pool, checkpointer
