from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "local"
    mock_mode: bool = True
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/investment_ai"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "development-only-change-me"
    jwt_issuer: str = "investment-platform"
    jwt_audience: str = "investment-api"
    access_token_ttl_minutes: int = 30
    max_research_lookback_days: int = 365
    review_required: bool = True

settings = Settings()
