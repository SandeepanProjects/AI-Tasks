# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):

#     APP_NAME: str

#     ENVIRONMENT: str

#     POSTGRES_HOST: str
#     POSTGRES_PORT: int
#     POSTGRES_DB: str
#     POSTGRES_USER: str
#     POSTGRES_PASSWORD: str

#     REDIS_HOST: str
#     REDIS_PORT: int

#     QDRANT_HOST: str
#     QDRANT_PORT: int

#     class Config:
#         env_file = ".env"


# settings = Settings()


# app/config/settings.py

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True
    )

    APP_NAME: str = "Enterprise Financial Advisor Copilot"

    ENVIRONMENT: str = "development"

    DEBUG: bool = False

    # =========================
    # Database
    # =========================

    DATABASE_URL: str

    # =========================
    # Redis
    # =========================

    REDIS_URL: str

    # =========================
    # Qdrant
    # =========================

    QDRANT_URL: str

    QDRANT_COLLECTION: str = "financial_documents"

    # =========================
    # OpenAI
    # =========================

    OPENAI_API_KEY: str

    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    OPENAI_EMBEDDING_MODEL: str = (
        "text-embedding-3-large"
    )

    # =========================
    # JWT
    # =========================

    JWT_SECRET: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # =========================
    # MLflow
    # =========================

    MLFLOW_TRACKING_URI: str = (
        "http://localhost:5000"
    )


@lru_cache
def get_settings():

    return Settings()


settings = get_settings()