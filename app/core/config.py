from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env."""

    environment: Literal["local", "dev", "prod"] = Field(default="local")

    app_name: str = Field(default="Lyra Quote Ask Agent")
    debug: bool = Field(default=True)

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/lyra.db",
        description="SQLAlchemy database URL. SQLite for local by default.",
    )

    # Base URL used for building external-facing links (e.g. checkout)
    base_url: str = Field(
        default="http://localhost:8000",
        description="Public base URL for external links (PoC).",
    )

    # Reserved for later integrations (Agents SDK, Telegram, etc.)
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4.1-mini")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

