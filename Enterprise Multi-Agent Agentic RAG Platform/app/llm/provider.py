from langchain_openai import ChatOpenAI

from app.config.settings import settings


def get_llm():

    return ChatOpenAI(
        model=settings.MODEL_NAME,
        temperature=0
    )