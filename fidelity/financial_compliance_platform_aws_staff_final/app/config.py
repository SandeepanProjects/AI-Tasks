from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env.runtime", ".env"), extra="ignore")
    app_env: str = "local"
    database_url: str
    sync_database_url: str
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    jwt_secret: str = Field(min_length=32)
    jwt_issuer: str = "financial-compliance-local"
    jwt_audience: str = "financial-compliance-api"
    openai_api_key: str = ""
    llm_provider: str = "openai"  # openai | bedrock
    embedding_provider: str = "openai"  # openai | bedrock
    aws_region: str = "ap-south-1"
    aws_s3_bucket: str = ""
    aws_s3_prefix: str = "compliance-documents"
    aws_kms_key_id: str = ""
    aws_bedrock_chat_model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    aws_bedrock_embedding_model_id: str = "amazon.titan-embed-text-v1"
    aws_bedrock_max_tokens: int = Field(default=4096, ge=256, le=8192)
    aws_bedrock_embedding_concurrency: int = Field(default=4, ge=1, le=16)
    aws_textract_poll_seconds: int = Field(default=5, ge=1, le=30)
    aws_textract_max_wait_seconds: int = Field(default=600, ge=30, le=3600)
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = Field(default=1536, ge=1536, le=1536)
    max_agent_steps: int = Field(default=8, ge=4, le=32)
    max_evaluation_reworks: int = Field(default=1, ge=0, le=3)
    outbox_poll_seconds: int = Field(default=5, ge=1, le=300)
    outbox_batch_size: int = Field(default=100, ge=1, le=1000)
    idempotency_key_max_length: int = Field(default=256, ge=1, le=1024)


settings = Settings()
