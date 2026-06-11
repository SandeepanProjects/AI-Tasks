from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    OPENAI_API_KEY: str

    QDRANT_HOST: str
    QDRANT_PORT: int

    MODEL_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()