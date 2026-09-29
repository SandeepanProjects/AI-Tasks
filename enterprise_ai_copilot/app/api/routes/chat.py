from fastapi import APIRouter, Depends
from app.api.dependencies import Principal, get_current_principal
from app.core.database import get_db
from app.graph.workflow import build_graph
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat(
    request: ChatRequest,
    principal: Principal = Depends(get_current_principal),
    db=Depends(get_db),
):
    graph = build_graph(db)
    config = {"configurable": {"thread_id": request.thread_id}}

    state = {
        "tenant_id": principal.tenant_id,
        "user_id": principal.user_id,
        "thread_id": request.thread_id,
        "question": request.message,
    }

    result = await graph.ainvoke(state, config=config)

    if "__interrupt__" in result:
        data = result["__interrupt__"][0].value
        return {
            "thread_id": request.thread_id,
            "status": "waiting_for_human",
            "answer": data["answer"],
            "requires_human_approval": True,
            "approval": data,
        }

    return {
        "thread_id": request.thread_id,
        "status": "completed",
        "answer": result.get("answer"),
        "requires_human_approval": False,
    }
