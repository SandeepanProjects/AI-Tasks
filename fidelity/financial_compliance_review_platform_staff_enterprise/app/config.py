from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "local"
    database_url: str
    sync_database_url: str
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    jwt_secret: str
    jwt_issuer: str = "financial-compliance-local"
    jwt_audience: str = "financial-compliance-api"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    max_agent_steps: int = 8
    max_evaluation_reworks: int = 1


settings = Settings()
