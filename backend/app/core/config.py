from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://football:football_secret@db:5432/football_analytics"
    database_url_sync: str = "postgresql://football:football_secret@db:5432/football_analytics"
    environment: str = "development"
    backend_port: int = 7860
    backend_host: str = "0.0.0.0"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
