from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.client = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )

    async def embed(self, text: str) -> list[float]:
        return await self.client.aembed_query(text)

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        return await self.client.aembed_documents(texts)
