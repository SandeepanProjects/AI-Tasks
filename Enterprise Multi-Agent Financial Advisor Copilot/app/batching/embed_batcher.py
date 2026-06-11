from openai import OpenAI
from app.core.config import settings


class EmbedBatcher:

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def embed_batch(self, texts: list):

        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts
        )

        return [
            item.embedding
            for item in response.data
        ]