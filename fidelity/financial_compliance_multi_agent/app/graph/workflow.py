from langgraph.graph import StateGraph,START,END
from app.graph.state import ComplianceState
from app.agents.claim_extraction import ClaimExtractionAgent
from app.agents.policy_research import PolicyResearchAgent
from app.agents.compliance_analysis import ComplianceAnalysisAgent
from app.agents.risk_assessment import RiskAssessmentAgent
from app.guardrails.output_validation import validate_result
claim_agent=ClaimExtractionAgent(); research_agent=PolicyResearchAgent(); analysis_agent=ComplianceAnalysisAgent(); risk_agent=RiskAssessmentAgent()
async def extract_claims(s): return {"claims":await claim_agent.run(s["content"])}
async def research_policies(s): return {"research":await research_agent.run(s["db"],s["tenant_id"],s["claims"])}
async def analyze(s): return {"analysis":await analysis_agent.run(s["content"],s["claims"],s["research"])}
def risk(s): return {"analysis":risk_agent.run(s["analysis"])}
def guard(s):
    allowed={int(p["policy_id"]) for p in s["research"].get("policies",[])}
    result=validate_result({**s["analysis"],"claims":s["claims"],"metadata":{"agent_sequence":["claim_extraction","policy_research","compliance_analysis","risk_assessment"]}},allowed)
    return {"result":result}
b=StateGraph(ComplianceState)
for name,fn in [("extract_claims",extract_claims),("research_policies",research_policies),("analyze",analyze),("risk",risk),("guardrails",guard)]: b.add_node(name,fn)
b.add_edge(START,"extract_claims"); b.add_edge("extract_claims","research_policies"); b.add_edge("research_policies","analyze"); b.add_edge("analyze","risk"); b.add_edge("risk","guardrails"); b.add_edge("guardrails",END)
compliance_graph=b.compile()
async def run_compliance_graph(review_id,tenant_id,content,db): return await compliance_graph.ainvoke({"review_id":review_id,"tenant_id":tenant_id,"content":content,"db":db})
