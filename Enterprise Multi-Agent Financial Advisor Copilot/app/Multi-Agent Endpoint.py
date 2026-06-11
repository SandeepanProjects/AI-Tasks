from fastapi import APIRouter, Depends

from app.enterprise.auth.security import get_current_user
from app.enterprise.rbac.middleware import RBACMiddleware

from app.agents.graph import advisor_graph
from app.enterprise.audit.logger import AuditLogger


router = APIRouter()


@router.post("/secure/agents/run")
def run_agents(
    request: dict,
    user=Depends(get_current_user)
):

    RBACMiddleware.check_permission(
        user,
        "run_agents"
    )

    AuditLogger.log(
        user["user_id"],
        "run_agents",
        request
    )

    state = {
        "query": request["query"],
        "portfolio_data":
        request.get("portfolio_data", {})
    }

    result = advisor_graph.invoke(state)

    AuditLogger.log(
        user["user_id"],
        "agent_result",
        {"output": result["final_report"]}
    )

    return result