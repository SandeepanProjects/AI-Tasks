import httpx
import ast
import json
from typing import Any, Protocol
from app.core.config import settings
from app.core.metrics import LLM_CALLS, LLM_LATENCY, LLM_TOKENS

class ChatModel(Protocol):
    async def structured_completion(self, *, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]: ...

class MockChatModel:
    async def structured_completion(self, *, system, user, schema):
        try:
            payload = json.loads(user)
            ids = payload.get("evidence_ids", [])
        except Exception:
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
        payload={"model":self.model,"temperature":0,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
                 "response_format":{"type":"json_schema","json_schema":{"name":"research_report","strict":True,"schema":schema}}}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with LLM_LATENCY.labels(self.model).time():
                    r=await client.post(f"{self.base_url}/chat/completions",json=payload,
                                        headers={"Authorization":f"Bearer {self.api_key}"})
                r.raise_for_status()
                data=r.json()
                usage = data.get("usage", {})
                for kind, field in (("prompt", "prompt_tokens"), ("completion", "completion_tokens"), ("total", "total_tokens")):
                    if usage.get(field) is not None:
                        LLM_TOKENS.labels(self.model, kind).inc(int(usage[field]))
                content = data["choices"][0]["message"].get("content")
                if not content:
                    raise ValueError("LLM returned an empty structured response")
                result=json.loads(content)
                if not isinstance(result, dict):
                    raise ValueError("LLM response must be a JSON object")
                LLM_CALLS.labels(self.model,"success").inc()
                return result
        except Exception:
            LLM_CALLS.labels(self.model,"error").inc()
            raise
