from langgraph.graph import StateGraph
from langgraph.graph import END

from app.agents.state import AgentState

from app.agents.planner import planner_node
from app.agents.rag_agent import rag_node
from app.agents.research import research_node
from app.agents.critic import critic_node
from app.workflows.router import (
    route_task
)

def routing_function(state):

    return route_task(
        state["question"]
    )

builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)

builder.add_node("rag", rag_node)

builder.add_node("research", research_node)

builder.add_node("critic", critic_node)

builder.set_entry_point("planner")

builder.add_edge("planner", "rag")

builder.add_edge("rag", "research")

builder.add_edge("research", "critic")

builder.add_edge("critic", END)

builder.add_conditional_edges(
    "planner",
    routing_function,
    {
        "rag": "rag",
        "sql": "sql_agent",
        "memory": "memory_agent",
        "general": "research"
    }
)

graph = builder.compile()