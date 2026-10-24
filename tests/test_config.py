"""Smoke tests: the package imports and configuration loads with valid defaults."""

from carbon_elt.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Settings load with valid default values."""
    settings = Settings()
    assert settings.carbon_api_base_url.startswith("https://")
    assert settings.duckdb_path.endswith(".duckdb")
    assert settings.request_timeout_seconds > 0


def test_get_settings_is_cached() -> None:
    """Settings instance is cached and reused."""
    assert get_settings() is get_settings()
