from functools import lru_cache
from pydantic import Field, SecretStr, field_validator, model_validator
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
    auth_mode: str = "local_jwt"
    oidc_jwks_url: str | None = None
    jwt_secret: SecretStr = SecretStr("")
    access_token_ttl_minutes: int = Field(default=30, ge=5, le=1440)
    max_research_lookback_days: int = Field(default=365, ge=1, le=3650)
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    embedding_model: str | None = None
    cors_origins: list[str] = Field(default_factory=list)
    embedding_dimensions: int = Field(default=384, ge=64, le=4096)
    max_context_chunks: int = Field(default=8, ge=1, le=50)
    max_tool_calls: int = Field(default=8, ge=1, le=32)
    request_timeout_seconds: float = Field(default=30, gt=0, le=120)

    @model_validator(mode="after")
    def validate_production_configuration(self):
        if self.auth_mode == "oidc" and not self.oidc_jwks_url:
            raise ValueError("AUTH_MODE=oidc requires OIDC_JWKS_URL")
        if self.app_env.lower() in {"production", "prod"}:
            if self.mock_mode:
                raise ValueError("MOCK_MODE must be false in production")
            if self.auth_mode != "oidc" or not self.oidc_jwks_url:
                raise ValueError("Production authentication requires AUTH_MODE=oidc and OIDC_JWKS_URL")
            if not self.oidc_jwks_url.startswith("https://"):
                raise ValueError("Production OIDC_JWKS_URL must use HTTPS")
            if not (self.llm_base_url and self.llm_api_key and self.llm_api_key.get_secret_value().strip()
                    and self.llm_model and self.embedding_model):
                raise ValueError("Production requires chat and embedding provider configuration")
        return self

    @field_validator("auth_mode")
    @classmethod
    def validate_auth_mode(cls, value):
        if value not in {"local_jwt", "oidc"}:
            raise ValueError("AUTH_MODE must be local_jwt or oidc")
        return value

    @field_validator("embedding_dimensions")
    @classmethod
    def validate_embedding_dimensions(cls, value):
        # The pgvector column and migrations use Vector(384). Changing this requires a migration.
        if value != 384:
            raise ValueError("EMBEDDING_DIMENSIONS is fixed at 384; change the vector column via migration first")
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
