from app.agents.planner import Planner


def test_planner_respects_max_steps_and_keeps_policy_research():
    tasks = Planner().plan(2)
    assert 1 <= len(tasks) <= 2
    assert any(task["kind"] == "policy_research" for task in tasks)


def test_planner_selects_specialists_from_submission_signals():
    tasks = Planner().plan(4, "This portfolio has fees, volatility risk and annualized performance claims")
    kinds = {task["kind"] for task in tasks}
    assert {"policy_research", "fees", "risk", "performance"} <= kinds
