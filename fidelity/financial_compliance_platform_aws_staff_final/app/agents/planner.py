"""Workflow adapter for the content-adaptive enterprise planner."""
from app.enterprise.planning import AdaptivePlanner

class Planner:
    def __init__(self, max_tasks: int = 4):
        self.adaptive = AdaptivePlanner(max_tasks=max_tasks)

    def plan(self, max_steps: int, statement: str = "", *, has_portfolio: bool = False):
        plan = self.adaptive.plan(statement, has_portfolio=has_portfolio)
        # The current graph has four implemented specialist agents. Domain modules
        # such as portfolio analytics are invoked by their dedicated service, not
        # dispatched to an agent that does not exist in this graph.
        supported = {"policy_research", "performance", "risk", "fees"}
        tasks = [t for t in plan.tasks if t.kind in supported][:max_steps]
        if not any(t.kind == "policy_research" for t in tasks):
            from uuid import uuid4
            tasks.append(type("Task", (), {"task_id": f"policy_research-{uuid4().hex[:8]}", "kind": "policy_research", "objective": "Resolve applicable policy clauses"})())
        return [{"task_id": t.task_id, "kind": t.kind, "status": "pending", "objective": t.objective}
                for t in tasks[:max_steps]]
