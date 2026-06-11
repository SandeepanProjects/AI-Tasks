from fastapi import APIRouter

from pydantic import BaseModel

from app.agents.graph import advisor_graph


router = APIRouter()


class AgentRequest(BaseModel):

    query: str

    portfolio_data: dict | None = None


@router.post("/agents/run")
def run_agents(req: AgentRequest):

    state = {
        "query": req.query,
        "portfolio_data": req.portfolio_data or {}
    }

    result = advisor_graph.invoke(state)

    return {
        "final_report": result["final_report"]
    }