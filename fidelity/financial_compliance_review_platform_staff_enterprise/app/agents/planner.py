from uuid import uuid4

KINDS = ("policy_research", "performance", "risk", "fees")


class Planner:
    def plan(self, max_steps):
        return [
            {
                "task_id": f"{k}-{uuid4().hex[:8]}",
                "kind": k,
                "status": "pending",
                "objective": f"Assess {k} claims against retrieved policy evidence",
            }
            for k in KINDS[:max_steps]
        ]
