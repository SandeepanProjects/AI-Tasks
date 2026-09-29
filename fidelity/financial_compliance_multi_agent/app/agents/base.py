import json
from openai import AsyncOpenAI
from app.core.config import settings
class AgentBase:
    def __init__(self): self.client=AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    async def json_completion(self,system,user,fallback):
        if not self.client: return fallback()
        response=await self.client.chat.completions.create(model=settings.openai_model,response_format={"type":"json_object"},messages=[{"role":"system","content":system},{"role":"user","content":user}],temperature=0.1)
        return json.loads(response.choices[0].message.content or "{}")
