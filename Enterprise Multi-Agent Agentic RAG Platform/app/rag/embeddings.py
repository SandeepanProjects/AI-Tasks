from langchain_openai import OpenAIEmbeddings

from app.config.settings import settings


_embeddings = None


def get_embeddings():

    global _embeddings

    if _embeddings is None:

        _embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-large"
        )

    return _embeddings