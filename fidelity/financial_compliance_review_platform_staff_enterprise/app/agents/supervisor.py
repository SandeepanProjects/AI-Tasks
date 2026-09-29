ALLOWED = {"policy_research", "performance", "risk", "fees"}


class Supervisor:
    def __init__(self, max_steps):
        self.max_steps = max_steps

    def route(self, tasks, done, steps):
        if steps >= self.max_steps:
            return []
        return [t for t in tasks if t["task_id"] not in done and t["kind"] in ALLOWED][
            : self.max_steps - steps
        ]
