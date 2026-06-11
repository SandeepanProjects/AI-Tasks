from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):

    query: str

    context: str

    portfolio_data: Dict[str, Any]

    research: str

    risk_analysis: str

    compliance_notes: List[str]

    final_report: str