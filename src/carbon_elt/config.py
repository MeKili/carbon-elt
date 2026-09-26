"""Application configuration for the carbon-elt pipeline."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings, loaded from the environment or an optional ``.env`` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    carbon_api_base_url: str = Field(
        "https://api.carbonintensity.org.uk",
        description="Base URL for the UK Carbon Intensity API",
    )
    duckdb_path: str = Field(
        "data/carbon.duckdb",
        description="Local filesystem path to the DuckDB database file",
    )
    request_timeout_seconds: float = Field(
        10.0,
        description="HTTP request timeout in seconds",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (configuration is read once)."""
    return Settings()
