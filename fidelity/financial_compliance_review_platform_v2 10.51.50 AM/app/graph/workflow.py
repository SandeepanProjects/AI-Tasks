import asyncio
from langgraph.graph import StateGraph, START, END
from app.agents.planner import Planner
from app.agents.supervisor import Supervisor
from app.agents.specialists import (
    PerformanceAgent,
    RiskAgent,
    FeesAgent,
    PolicyResearchAgent,
)
from app.agents.evaluator import evaluate
from app.domain.schemas import AgentInput
from app.guardrails import validate


class Workflow:
    def __init__(self, policy_loader, max_steps=8, max_reworks=1):
        self.loader = policy_loader
        self.max_steps = max_steps
        self.max_reworks = max_reworks
        self.agents = {
            a.name: a
            for a in (
                PerformanceAgent(),
                RiskAgent(),
                FeesAgent(),
                PolicyResearchAgent(),
            )
        }
        g = StateGraph(dict)
        for name, fn in [
            ("retrieve", self.retrieve),
            ("plan", self.plan),
            ("dispatch", self.dispatch),
            ("evaluate", self.eval),
            ("guardrails", self.guardrails),
            ("human", self.human),
            ("failed", self.failed),
        ]:
            g.add_node(name, fn)
        g.add_edge(START, "retrieve")
        g.add_edge("retrieve", "plan")
        g.add_edge("plan", "dispatch")
        g.add_conditional_edges(
            "dispatch",
            self.after_dispatch,
            {"evaluate": "evaluate", "failed": "failed"},
        )
        g.add_conditional_edges(
            "evaluate",
            self.after_eval,
            {"guardrails": "guardrails", "dispatch": "dispatch", "failed": "failed"},
        )
        g.add_conditional_edges(
            "guardrails", self.after_guardrails, {"human": "human", "failed": "failed"}
        )
        g.add_edge("human", END)
        g.add_edge("failed", END)
        self.graph = g.compile()

    async def retrieve(self, s):
        policies = await self.loader(s["tenant_id"], s["statement"])
        return {
            "policies": policies,
            "policy_versions": {p["id"]: p["version"] for p in policies},
            "step_count": 0,
            "rework": 0,
            "outputs": {},
            "errors": [],
        }

    async def plan(self, s):
        tasks = Planner().plan(s.get("max_steps", self.max_steps))
        return {"tasks": tasks, "task_status": {t["task_id"]: "pending" for t in tasks}}

    async def dispatch(self, s):
        todo = Supervisor(s.get("max_steps", self.max_steps)).route(
            s["tasks"], set(s["outputs"]), s["step_count"]
        )

        async def one(t):
            inp = AgentInput(
                review_id=s["review_id"],
                tenant_id=s["tenant_id"],
                statement=s["statement"],
                policies=s["policies"],
                task_id=t["task_id"],
            )
            return t["task_id"], await self.agents[t["kind"]].run(inp)

        results = await asyncio.gather(*(one(t) for t in todo), return_exceptions=True)
        outputs = dict(s["outputs"])
        status = dict(s["task_status"])
        errors = list(s["errors"])
        for t, r in zip(todo, results):
            if isinstance(r, Exception):
                status[t["task_id"]] = "failed"
                errors.append(f'{t["kind"]}:{type(r).__name__}')
            else:
                tid, out = r
                outputs[tid] = out.model_dump()
                status[tid] = "completed"
        return {
            "outputs": outputs,
            "task_status": status,
            "errors": errors,
            "step_count": s["step_count"] + len(todo),
        }

    def after_dispatch(self, s):
        if s["errors"] or s["step_count"] >= s.get("max_steps", self.max_steps):
            return "evaluate"
        return "evaluate"

    def eval(self, s):
        result = evaluate(s["outputs"])
        updates = {"evaluation": result}
        if not result["passed"] and s["rework"] < s.get(
            "max_reworks", self.max_reworks
        ):
            updates["rework"] = s["rework"] + 1
        return updates

    def after_eval(self, s):
        if s["evaluation"]["passed"]:
            return "guardrails"
        if s["rework"] < s.get("max_reworks", self.max_reworks):
            # One bounded rework: clear failed/missing task state; failed tasks are retried next dispatch.
            done = set(s["outputs"])
            for t in s["tasks"]:
                if t["task_id"] not in done:
                    s["task_status"][t["task_id"]] = "pending"
            return "dispatch"
        return "failed"

    def guardrails(self, s):
        findings = [f for o in s["outputs"].values() for f in o["findings"]]
        try:
            validate(findings, s["policies"], s["tenant_id"])
        except Exception as e:
            return {
                "guardrail_passed": False,
                "errors": s["errors"] + [str(e)],
                "final_result": {"findings": findings},
            }
        findings.sort(key=lambda f: (f["category"], f["severity"], f["statement"]))
        return {
            "guardrail_passed": True,
            "findings": findings,
            "final_result": {
                "findings": findings,
                "evaluation": s["evaluation"],
                "policy_versions": s["policy_versions"],
            },
            "status": "needs_human",
        }

    def after_guardrails(self, s):
        return "human" if s.get("guardrail_passed") else "failed"

    def human(self, s):
        return {"status": "needs_human"}

    def failed(self, s):
        return {
            "status": "failed",
            "final_result": {
                "errors": s["errors"],
                "evaluation": s.get("evaluation"),
                "guardrail_passed": False,
            },
        }
