from app.agents.evaluator import evaluate

def test_evaluator_requires_all_specialists_and_policy_context():
    result = evaluate({}, [], [])
    assert not result["passed"] and len(result["missing_agents"]) == 4
    assert not result["has_policy_context"]

def test_evaluator_rejects_findings_without_evidence():
    names = ("performance", "risk", "fees", "policy_research")
    outputs = {str(i): {"agent_name": name, "findings": []} for i, name in enumerate(names)}
    result = evaluate(outputs, [{"statement": "claim", "evidence": []}], [{"id": "p1"}])
    assert not result["passed"] and result["findings_without_evidence"] == ["claim"]
