# app/agents/agent.py


from app.agents.orchestrator import (
    AgentOrchestrator,
)

from app.agents.memory import (
    ConversationMemory,
)


class ProductionAgent:
    """
    Main production agent wrapper.

    Responsibilities:
    - memory management
    - orchestration
    - state handling
    - execution lifecycle
    """

    def __init__(self):
        self.memory = ConversationMemory()

        self.orchestrator = (
            AgentOrchestrator()
        )

    async def chat(
        self,
        user_query: str,
    ):
        """
        Main conversational entrypoint.
        """

        self.memory.add_message(
            role="user",
            content=user_query,
        )

        response = (
            await self.orchestrator.run(
                user_query=user_query,
                memory=self.memory,
            )
        )

        self.memory.add_message(
            role="assistant",
            content=response,
        )

        return {
            "response": response,
            "conversation_history": (
                self.memory.get_messages()
            ),
        }