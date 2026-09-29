import asyncio
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
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
from app.config import settings


class State(TypedDict, total=False):
    review_id: str
    tenant_id: str
    statement: str
    policies: list
    tasks: list
    task_status: dict
    outputs: dict
    errors: list
    step_count: int
    max_steps: int
    max_reworks: int
    rework: int
    evaluation: dict
    findings: list
    final_result: dict
    status: str
    guardrail_passed: bool
    human_decision: dict


class Workflow:
    def __init__(self, policy_loader, checkpointer):
        self.loader = policy_loader
        self.max_steps = settings.max_agent_steps
        self.max_reworks = settings.max_evaluation_reworks
        self.agents = {
            a.name: a
            for a in (
                PerformanceAgent(),
                RiskAgent(),
                FeesAgent(),
                PolicyResearchAgent(),
            )
        }
        g = StateGraph(State)
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
        self.graph = g.compile(checkpointer=checkpointer)

    async def retrieve(self, s):
        policies = await self.loader(s["tenant_id"], s["statement"])
        return {
            "policies": policies,
            "step_count": 0,
            "rework": 0,
            "outputs": {},
            "errors": [],
        }

    async def plan(self, s):
        tasks = Planner().plan(min(s.get("max_steps", self.max_steps), 4))
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
        return "failed" if s["errors"] else "evaluate"

    async def eval(self, s):
        findings = [f for o in s["outputs"].values() for f in o["findings"]]
        result = evaluate(s["outputs"], findings, s["policies"])
        return {"evaluation": result, "findings": findings}

    def after_eval(self, s):
        if s["evaluation"]["passed"]:
            return "guardrails"
        if s["rework"] < s.get("max_reworks", self.max_reworks):
            return "dispatch"
        return "failed"

    async def guardrails(self, s):
        try:
            validate(s["findings"], s["policies"], s["tenant_id"])
            findings = sorted(
                s["findings"],
                key=lambda f: (f["category"], f["severity"], f["statement"]),
            )
            return {
                "guardrail_passed": True,
                "findings": findings,
                "final_result": {
                    "findings": findings,
                    "evaluation": s["evaluation"],
                    "policy_versions": sorted({p["version"] for p in s["policies"]}),
                },
                "status": "needs_human",
            }
        except Exception as exc:
            return {
                "guardrail_passed": False,
                "errors": s["errors"] + [f"guardrail:{type(exc).__name__}"],
            }

    def after_guardrails(self, s):
        return "human" if s.get("guardrail_passed") else "failed"

    async def human(self, s):
        decision = interrupt(
            {
                "kind": "compliance_review",
                "review_id": s["review_id"],
                "assessment": s.get("final_result"),
                "message": "Reviewer decision required",
            }
        )
        if not isinstance(decision, dict) or decision.get("decision") not in (
            "approve",
            "reject",
        ):
            raise ValueError("Invalid HITL resume payload")
        result = {**(s.get("final_result") or {}), "human_decision": decision}
        return {
            "human_decision": decision,
            "final_result": result,
            "status": "approved" if decision["decision"] == "approve" else "rejected",
        }

    async def failed(self, s):
        return {
            "status": "failed",
            "final_result": {
                "errors": s.get("errors", []),
                "evaluation": s.get("evaluation"),
            },
        }
