from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore",
    )

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_RELOAD: bool = False
    API_URL: str = "http://localhost:8000"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/server"

    CLIENT_WORKERS: int = Field(default=5, ge=1)
    CLIENT_MAX_DELAY_MS: int = Field(default=1000, ge=0)
    CLIENT_REQUESTS_PER_WORKER: int = Field(default=10, ge=1)
    CLIENT_LOG_FILE: str = "client/logs/client.log"
    CLIENT_REQUEST_TIMEOUT_SECONDS: float = Field(default=5.0, gt=0)
    CLIENT_MAX_ATTEMPTS: int = Field(default=3, ge=1)
    CLIENT_RETRY_BACKOFF_MS: int = Field(default=200, ge=0)


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
