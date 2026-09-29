from fastapi import APIRouter, Depends
from pydantic import BaseModel
from langgraph.types import Command

from app.api.dependencies import Principal, get_current_principal
from app.core.database import get_db
from app.graph.workflow import build_graph

router = APIRouter(prefix="/hitl", tags=["hitl"])

class HITLDecision(BaseModel):
    approved: bool
    comment: str = ""

@router.post("/{thread_id}/resume")
async def resume(
    thread_id: str,
    decision: HITLDecision,
    principal: Principal = Depends(get_current_principal),
    db=Depends(get_db),
):
    result = await build_graph(db).ainvoke(
        Command(resume={
            "approved": decision.approved,
            "comment": decision.comment,
            "reviewer": principal.user_id,
        }),
        config={"configurable": {"thread_id": thread_id}},
    )

    return {
        "thread_id": thread_id,
        "status": "completed",
        "answer": result.get("answer"),
        "decision": decision.model_dump(),
    }
