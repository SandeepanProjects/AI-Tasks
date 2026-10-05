from dataclasses import dataclass, field
from typing import Any, Protocol

@dataclass
class AgentContext:
    request_id: str
    tenant_id: str
    input: dict[str, Any]
    state: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResult:
    agent: str
    output: dict[str, Any]
    next_step: str | None = None

class Agent(Protocol):
    name: str
    async def run(self, context: AgentContext) -> AgentResult:
        ...

class Planner(Protocol):
    async def plan(self, context: AgentContext) -> list[str]:
        ...

class Supervisor(Protocol):
    async def next_step(self, context: AgentContext, completed: list[str]) -> str:
        ...

class Evaluator(Protocol):
    async def evaluate(self, context: AgentContext) -> tuple[bool, str]:
        ...
