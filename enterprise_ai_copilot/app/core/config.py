from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "enterprise-ai-copilot"
    environment: str = "development"
    api_v1_prefix: str = "/v1"

    database_url: str
    sync_database_url: str
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    max_input_chars: int = 8000
    cache_ttl_seconds: int = 120
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    hitl_risk_threshold: float = 0.80

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
