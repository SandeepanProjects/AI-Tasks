from .contracts import Agent, AgentContext, AgentResult

class AgentRuntime:
    """Generic bounded executor. It knows no financial business rules."""

    def __init__(self, agents: dict[str, Agent], max_steps: int = 10):
        self.agents = agents
        self.max_steps = max_steps

    async def execute(self, context: AgentContext, steps: list[str]) -> list[AgentResult]:
        results = []
        for step in steps[:self.max_steps]:
            result = await self.agents[step].run(context)
            results.append(result)
            context.state[step] = result.output
        return results
