"""Tests for the command-line interface."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from carbon_elt.cli import cmd_info, cmd_load, cmd_load_generation, main


def test_cmd_load_calls_pipeline() -> None:
    """Test that load command calls the pipeline."""
    with patch("carbon_elt.cli.run") as mock_run:
        mock_run.return_value = {"intensity": 42, "generation": 28}
        result = cmd_load(MagicMock())
        assert result == 0
        mock_run.assert_called_once()


def test_cmd_load_generation_loads_data() -> None:
    """Test that load_generation command fetches and loads generation data."""
    with (
        patch("carbon_elt.cli.fetch_generation") as mock_fetch,
        patch("carbon_elt.cli.get_connection") as mock_conn,
        patch("carbon_elt.cli.get_settings") as mock_settings,
    ):
        mock_settings.return_value.duckdb_path = ":memory:"
        mock_fetch.return_value = []
        mock_connection = MagicMock()
        mock_conn.return_value = mock_connection

        result = cmd_load_generation(MagicMock())
        assert result == 0
        mock_fetch.assert_called_once()


def test_cmd_info_shows_config() -> None:
    """Test that info command shows configuration."""
    with patch("carbon_elt.cli.get_settings") as mock_settings:
        mock_settings.return_value.duckdb_path = "/tmp/test.duckdb"
        mock_settings.return_value.carbon_api_base_url = "https://example.com"
        mock_settings.return_value.request_timeout_seconds = 5.0

        result = cmd_info(MagicMock())
        assert result == 0


def test_main_with_load_command() -> None:
    """Test main function with load command."""
    with patch("carbon_elt.cli.cmd_load") as mock_cmd:
        mock_cmd.return_value = 0
        result = main(["load"])
        assert result == 0


def test_main_with_no_args_prints_help() -> None:
    """Test main function with no arguments shows help."""
    result = main([])
    assert result == 0


def test_main_with_info_command() -> None:
    """Test main function with info command."""
    with patch("carbon_elt.cli.cmd_info") as mock_cmd:
        mock_cmd.return_value = 0
        result = main(["info"])
        assert result == 0


def test_main_with_unknown_command() -> None:
    """Test main function with unknown command."""
    with pytest.raises(SystemExit):
        main(["unknown"])
