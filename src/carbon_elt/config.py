"""Application configuration for the carbon-elt pipeline."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings, loaded from the environment or an optional ``.env`` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    carbon_api_base_url: str = "https://api.carbonintensity.org.uk"
    duckdb_path: str = "data/carbon.duckdb"
    request_timeout_seconds: float = 10.0


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (configuration is read once)."""
    return Settings()
