from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore",
    )

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/server"

@lru_cache
def get_settings() -> "Settings":
    return Settings()

settings = get_settings()
