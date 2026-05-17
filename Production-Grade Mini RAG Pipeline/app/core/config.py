from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    EMBEDDING_MODEL: str
    CHAT_MODEL: str

    class Config:
        env_file = ".env"

    settings = Settings()