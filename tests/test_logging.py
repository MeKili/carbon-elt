"""Tests for structured logging configuration."""

from __future__ import annotations

from carbon_elt.logging_config import get_logger, setup_logging


def test_setup_logging_configures_structlog() -> None:
    """Test that setup_logging configures structlog without errors."""
    setup_logging(log_level="INFO")


def test_get_logger_returns_logger() -> None:
    """Test that get_logger returns a logger instance."""
    logger = get_logger("test_module")
    assert logger is not None
    assert callable(logger.info)
