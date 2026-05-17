# tests/test_agent.py

import pytest

from app.agents.agent import (
    ProductionAgent,
)


@pytest.mark.asyncio
async def test_agent_chat():
    agent = ProductionAgent()

    response = await agent.chat(
        "What is AI?"
    )

    assert response is not None

    assert "response" in response
