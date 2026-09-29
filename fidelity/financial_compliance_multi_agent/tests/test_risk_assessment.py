from app.agents.risk_assessment import RiskAssessmentAgent
def test_high_risk():
    r=RiskAssessmentAgent().run({"findings":[{"status":"potential_violation"}]})
    assert r["overall_risk"]=="high" and r["recommended_action"]=="block_and_escalate"
def test_empty_defaults_medium(): assert RiskAssessmentAgent().run({"findings":[]})["overall_risk"]=="medium"
