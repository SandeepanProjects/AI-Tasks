from fastapi import APIRouter

from pydantic import BaseModel

from app.agents.orchestrator import (
    AgentOrchestrator,
)

router = APIRouter()

agent = AgentOrchestrator()


class AgentRequest(BaseModel):
    query: str


@router.post("/agent")
async def run_agent(
    request: AgentRequest,
):
    response = await agent.run(
        request.query
    )

    return {
        "response": response
    }