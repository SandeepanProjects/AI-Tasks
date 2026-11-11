"""Content-adaptive planning with a deterministic policy boundary."""
from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

ALLOWED_TASKS = {"policy_research", "claim_verification", "performance", "risk", "fees", "portfolio", "regulatory"}

@dataclass(frozen=True)
class PlannedTask:
    task_id: str
    kind: str
    objective: str
    priority: int

@dataclass(frozen=True)
class AdaptivePlan:
    tasks: tuple[PlannedTask, ...]
    risk_tier: str
    rationale: tuple[str, ...]

class AdaptivePlanner:
    """Rules select a minimal task set; an LLM may propose, never authorize, tasks."""
    def __init__(self, max_tasks: int = 6):
        if not 1 <= max_tasks <= 7:
            raise ValueError("max_tasks must be between 1 and 7")
        self.max_tasks = max_tasks

    def plan(self, submission: str, *, has_portfolio: bool = False, has_market_data: bool = False) -> AdaptivePlan:
        text = submission.casefold()
        selected: list[tuple[str, int, str]] = [("claim_verification", 1, "Verify each material claim against approved evidence")]
        rationale = ["Claim verification is mandatory for every submission"]
        signals = {
            "risk": ("risk", "volatile", "loss", "drawdown", "guarantee", "capital protection"),
            "fees": ("fee", "commission", "expense ratio", "charge", "cost"),
            "performance": ("return", "performance", "yield", "benchmark", "annualized"),
            "regulatory": ("regulation", "regulatory", "sec", "finra", "disclosure", "suitability"),
        }
        for kind, terms in signals.items():
            if any(term in text for term in terms):
                selected.append((kind, 2, f"Assess {kind} statements and applicable controls"))
                rationale.append(f"{kind} specialist selected from submission signals")
        if has_portfolio:
            selected.append(("portfolio", 1, "Analyze portfolio exposures and scenario sensitivities"))
            rationale.append("Portfolio context supplied")
        if has_market_data:
            selected.append(("performance", 2, "Validate market-sensitive claims against approved dated data"))
            rationale.append("Approved market data supplied")
        selected.append(("policy_research", 3, "Resolve applicable policy clauses and version conflicts"))
        # De-duplicate while preserving the strongest priority.
        by_kind = {}
        for kind, priority, objective in selected:
            if kind not in ALLOWED_TASKS:
                continue
            if kind not in by_kind or priority < by_kind[kind][0]:
                by_kind[kind] = (priority, objective)
        ordered = sorted(by_kind.items(), key=lambda item: (item[1][0], item[0]))[:self.max_tasks]
        tasks = tuple(PlannedTask(f"{kind}-{uuid4().hex[:10]}", kind, obj, priority)
                      for kind, (priority, obj) in ordered)
        high_terms = ("guaranteed", "risk-free", "cannot lose", "suitable for all", "guaranteed return")
        risk_tier = "high" if any(term in text for term in high_terms) else ("medium" if len(tasks) >= 4 else "low")
        return AdaptivePlan(tasks, risk_tier, tuple(rationale))

    @staticmethod
    def validate_proposal(proposed: list[dict], *, max_tasks: int = 6) -> list[dict]:
        """Validate model-proposed tasks against allowlist and hard resource limits."""
        if len(proposed) > max_tasks:
            raise ValueError("planner exceeded task budget")
        clean = []
        seen = set()
        for task in proposed:
            kind = task.get("kind")
            if kind not in ALLOWED_TASKS:
                raise ValueError(f"unsupported task kind: {kind}")
            if kind in seen:
                continue
            seen.add(kind)
            clean.append({"kind": kind, "objective": str(task.get("objective", ""))[:500]})
        return clean
