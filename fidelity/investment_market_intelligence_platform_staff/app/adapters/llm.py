import httpx
import ast
from typing import Any, Protocol
from app.core.config import settings
from app.core.metrics import LLM_CALLS

class ChatModel(Protocol):
    async def structured_completion(self, *, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]: ...

class MockChatModel:
    async def structured_completion(self, *, system, user, schema):
        try:
            payload = ast.literal_eval(user)
            ids = payload.get("evidence_ids", [])
        except Exception:
            ids = []
        return {"summary":"Illustrative evidence-grounded analysis.",
                "observations":["Validate current licensed market data before use."],
                "risks":["Volatility","Liquidity","Model uncertainty"],
                "evidence_ids":ids[:1],"limitations":["Mock model; not investment advice."]}

class OpenAICompatibleChatModel:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float=30):
        self.base_url=base_url.rstrip("/")
        self.api_key=api_key
        self.model=model
        self.timeout=timeout
    async def structured_completion(self, *, system, user, schema):
        payload={"model":self.model,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
                 "response_format":{"type":"json_schema","json_schema":{"name":"research_report","strict":True,"schema":schema}}}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r=await client.post(f"{self.base_url}/chat/completions",json=payload,
                                    headers={"Authorization":f"Bearer {self.api_key}"})
                r.raise_for_status()
                data=r.json()
                import json
                result=json.loads(data["choices"][0]["message"]["content"])
                LLM_CALLS.labels(self.model,"success").inc()
                return result
        except Exception:
            LLM_CALLS.labels(self.model,"error").inc()
            raise
