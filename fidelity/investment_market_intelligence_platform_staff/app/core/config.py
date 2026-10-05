from functools import lru_cache
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
    app_env: str = "local"
    mock_mode: bool = True
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/investment_ai"
    redis_url: str = "redis://localhost:6379/0"
    jwt_issuer: str = "investment-platform"
    jwt_audience: str = "investment-api"
    jwt_secret: SecretStr = SecretStr("")
    access_token_ttl_minutes: int = Field(default=30, ge=5, le=1440)
    max_research_lookback_days: int = Field(default=365, ge=1, le=3650)
    review_required: bool = True
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    embedding_dimensions: int = Field(default=384, ge=64, le=4096)
    max_context_chunks: int = Field(default=8, ge=1, le=50)
    max_tool_calls: int = Field(default=8, ge=1, le=32)
    request_timeout_seconds: float = Field(default=30, gt=0, le=120)

    @field_validator("jwt_secret")
    @classmethod
    def validate_secret(cls, v, info):
        if info.data.get("app_env") in {"production", "prod"} and len(v.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters in production")
        return v

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
