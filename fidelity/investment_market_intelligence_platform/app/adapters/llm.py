from typing import Protocol, Any

class ChatModel(Protocol):
    async def structured_completion(self, *, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]: ...

class MockChatModel:
    async def structured_completion(self, *, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        # Deterministic fixture. Production adapter must enforce timeout, token budget,
        # structured output, vendor policy, and redact sensitive inputs.
        return {
            "summary": "Illustrative analysis only. No live market data was queried.",
            "observations": ["Market conditions can change rapidly; validate with current licensed data."],
            "risks": ["Volatility", "Liquidity", "Data freshness", "Model uncertainty"],
            "evidence_ids": ["fixture-market-001"],
            "limitations": ["Mock model and fixture evidence; not investment advice."]
        }
