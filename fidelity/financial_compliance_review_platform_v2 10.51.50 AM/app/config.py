from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/compliance"
    auth_mode: str = "dev"
    jwt_issuer: str = ""
    jwt_audience: str = ""
    jwt_jwks_url: str = ""
    max_agent_steps: int = 8
    max_evaluation_reworks: int = 1
    otel_exporter_otlp_endpoint: str = ""


settings = Settings()
