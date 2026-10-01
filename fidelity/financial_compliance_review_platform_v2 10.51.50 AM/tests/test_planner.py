from app.agents.planner import Planner
from app.agents.supervisor import Supervisor


def test_plan_bounded():
    assert len(Planner().plan(2)) == 2


def test_disallowed_task_not_routed():
    assert Supervisor(3).route([{"task_id": "x", "kind": "evil"}], set(), 0) == []
