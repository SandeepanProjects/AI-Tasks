from openai import AsyncOpenAI
from app.core.config import settings
class EmbeddingService:
    def __init__(self): self.client=AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    async def embed(self,text):
        if not self.client: return None
        response=await self.client.embeddings.create(model=settings.embedding_model,input=text)
        return response.data[0].embedding
