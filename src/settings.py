import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent

    APP_BASE_URL: str = os.getenv(
        "APP_BASE_URL",
        "http://127.0.0.1:8000",
    )

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/url_shortener",
    )

    ENCRYPTION_KEY: str = os.getenv(
        "ENCRYPTION_KEY",
        "739f4e3c9d76864c17d5d5a6cc501fa4",
    )

    ENCRYPTION_TWEAK: str = os.getenv(
        "ENCRYPTION_TWEAK",
        "c3ec21e55fc633",
    )


def get_settings() -> Settings:
    return Settings()
