"""Tests for the command-line interface."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from carbon_elt.cli import (
    cmd_info,
    cmd_load,
    cmd_load_generation,
    cmd_load_regional,
    cmd_seed,
    cmd_status,
    cmd_test,
    cmd_transform,
    main,
)


def test_cmd_load_calls_pipeline() -> None:
    """Test that load command calls the pipeline."""
    with patch("carbon_elt.cli.run") as mock_run:
        mock_run.return_value = {"intensity": 42, "generation": 28, "regional": 15}
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


def test_cmd_load_regional_loads_data() -> None:
    """Test that load_regional command fetches and loads regional data."""
    with (
        patch("carbon_elt.cli.fetch_regional_intensity") as mock_fetch,
        patch("carbon_elt.cli.get_connection") as mock_conn,
        patch("carbon_elt.cli.get_settings") as mock_settings,
    ):
        mock_settings.return_value.duckdb_path = ":memory:"
        mock_fetch.return_value = []
        mock_connection = MagicMock()
        mock_conn.return_value = mock_connection

        result = cmd_load_regional(MagicMock())
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


def test_main_with_load_regional_command() -> None:
    """Test main function with load-regional command."""
    with patch("carbon_elt.cli.cmd_load_regional") as mock_cmd:
        mock_cmd.return_value = 0
        result = main(["load-regional"])
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


def test_cmd_status_shows_warehouse_stats() -> None:
    """Test that status command queries and displays warehouse statistics."""
    from carbon_elt.stats import TableStats

    with (
        patch("carbon_elt.cli.get_settings") as mock_settings,
        patch("carbon_elt.cli.get_connection") as mock_conn,
        patch("carbon_elt.cli.init_schema"),
        patch("carbon_elt.cli.get_all_stats") as mock_stats,
        patch("carbon_elt.cli.get_intensity_index_distribution") as mock_dist,
    ):
        mock_settings.return_value.duckdb_path = ":memory:"
        mock_connection = MagicMock()
        mock_conn.return_value = mock_connection
        mock_stats.return_value = {
            "raw_national_intensity": TableStats(
                "raw_national_intensity", 48, datetime(2025, 1, 1), datetime(2025, 1, 2)
            ),
            "raw_generation": TableStats("raw_generation", 0, None, None),
            "raw_regional_intensity": TableStats("raw_regional_intensity", 0, None, None),
        }
        mock_dist.return_value = {"moderate": 30, "high": 18}

        result = cmd_status(MagicMock())
        assert result == 0
        mock_stats.assert_called_once()
        mock_dist.assert_called_once()


def test_main_with_status_command() -> None:
    """Test main function with status command."""
    with patch("carbon_elt.cli.cmd_status") as mock_cmd:
        mock_cmd.return_value = 0
        result = main(["status"])
        assert result == 0


def test_main_with_unknown_command() -> None:
    """Test main function with unknown command."""
    with pytest.raises(SystemExit):
        main(["unknown"])


def test_cmd_transform_runs_dbt() -> None:
    """Test that transform command runs dbt models."""
    with patch("carbon_elt.cli.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Models built", stderr="")
        result = cmd_transform(MagicMock())
        assert result == 0
        mock_run.assert_called_once_with(
            ["dbt", "run"], capture_output=True, text=True, check=False
        )


def test_cmd_transform_handles_dbt_error() -> None:
    """Test that transform command reports dbt errors."""
    with patch("carbon_elt.cli.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="dbt error")
        result = cmd_transform(MagicMock())
        assert result == 1


def test_main_with_transform_command() -> None:
    """Test main function with transform command."""
    with patch("carbon_elt.cli.cmd_transform") as mock_cmd:
        mock_cmd.return_value = 0
        result = main(["transform"])
        assert result == 0


def test_cmd_test_runs_dbt() -> None:
    """Test that test command runs dbt tests."""
    with patch("carbon_elt.cli.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Tests passed", stderr="")
        result = cmd_test(MagicMock())
        assert result == 0
        mock_run.assert_called_once_with(
            ["dbt", "test"], capture_output=True, text=True, check=False
        )


def test_cmd_test_handles_dbt_error() -> None:
    """Test that test command reports dbt test failures."""
    with patch("carbon_elt.cli.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="test failed")
        result = cmd_test(MagicMock())
        assert result == 1


def test_cmd_seed_runs_dbt() -> None:
    """Test that seed command runs dbt seed."""
    with patch("carbon_elt.cli.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Seeds loaded", stderr="")
        result = cmd_seed(MagicMock())
        assert result == 0
        mock_run.assert_called_once_with(
            ["dbt", "seed"], capture_output=True, text=True, check=False
        )


def test_cmd_seed_handles_dbt_error() -> None:
    """Test that seed command reports dbt seed failures."""
    with patch("carbon_elt.cli.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="seed failed")
        result = cmd_seed(MagicMock())
        assert result == 1


def test_main_with_test_command() -> None:
    """Test main function with test command."""
    with patch("carbon_elt.cli.cmd_test") as mock_cmd:
        mock_cmd.return_value = 0
        result = main(["test"])
        assert result == 0


def test_main_with_seed_command() -> None:
    """Test main function with seed command."""
    with patch("carbon_elt.cli.cmd_seed") as mock_cmd:
        mock_cmd.return_value = 0
        result = main(["seed"])
        assert result == 0
