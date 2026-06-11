## LangGraph Workflow

## This is the orchestration layer.


from langgraph.graph import StateGraph

from app.agents.state import AgentState

from app.agents.supervisor import SupervisorAgent
from app.agents.portfolio_agent import PortfolioAgent
from app.agents.research_agent import ResearchAgent
from app.agents.risk_agent import RiskAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.report_agent import ReportAgent


portfolio = PortfolioAgent()
research = ResearchAgent()
risk = RiskAgent()
compliance = ComplianceAgent()
report = ReportAgent()


def portfolio_node(state): return portfolio.run(state)

def research_node(state): return research.run(state)

def risk_node(state): return risk.run(state)

def compliance_node(state): return compliance.run(state)

def report_node(state): return report.run(state)


graph = StateGraph(AgentState)

graph.add_node("portfolio", portfolio_node)

graph.add_node("research", research_node)

graph.add_node("risk", risk_node)

graph.add_node("compliance", compliance_node)

graph.add_node("report", report_node)


graph.set_entry_point("research")

graph.add_edge("research", "portfolio")

graph.add_edge("portfolio", "risk")

graph.add_edge("risk", "compliance")

graph.add_edge("compliance", "report")

graph.set_finish_point("report")


advisor_graph = graph.compile()