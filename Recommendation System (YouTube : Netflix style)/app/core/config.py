from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "recommendation-system"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    KAFKA_BROKER: str = "localhost:9092"

    TOP_K: int = 20

    class Config:
        env_file = ".env"


settings = Settings()