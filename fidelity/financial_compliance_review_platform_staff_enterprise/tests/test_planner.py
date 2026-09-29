from app.agents.planner import Planner


def test_planner_respects_max_steps():
    assert len(Planner().plan(2)) == 2
