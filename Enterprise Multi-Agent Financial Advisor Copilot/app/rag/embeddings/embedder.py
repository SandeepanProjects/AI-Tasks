from openai import OpenAI

from app.core.config import settings


class OpenAIEmbedder:

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def embed(
        self,
        text: str
    ):

        response = (
            self.client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
        )

        return (
            response.data[0].embedding
        )