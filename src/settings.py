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
        "postgresql+asyncpg://postgres:postgres@localhost:5432/online_cinema",
    )
