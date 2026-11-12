"""Bedrock embedding adapter. Titan Text Embeddings v1 returns 1536 dimensions."""
import asyncio
import json
from app.aws.clients import client
from app.config import settings


class BedrockEmbedder:
    def __init__(self):
        if settings.embedding_dimensions != 1536:
            raise RuntimeError("The current pgvector schema requires 1536 dimensions; use amazon.titan-embed-text-v1 or migrate the vector column")
        self.model_id = settings.aws_bedrock_embedding_model_id

    def _embed(self, text: str) -> list[float]:
        response = client("bedrock-runtime").invoke_model(
            modelId=self.model_id,
            body=json.dumps({"inputText": text}),
            accept="application/json", contentType="application/json")
        payload = json.loads(response["body"].read())
        vector = payload.get("embedding")
        if not isinstance(vector, list) or len(vector) != settings.embedding_dimensions:
            raise RuntimeError("Bedrock returned an embedding with an unexpected dimension")
        return vector

    async def embed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._embed, text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Bounded concurrency prevents exhausting Bedrock account/model quotas.
        semaphore = asyncio.Semaphore(settings.aws_bedrock_embedding_concurrency)
        async def one(text: str):
            async with semaphore:
                return await asyncio.to_thread(self._embed, text)
        return await asyncio.gather(*(one(text) for text in texts))
