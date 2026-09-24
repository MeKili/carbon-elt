"""Tests for Dagster assets (with mocked API calls)."""

from unittest.mock import MagicMock, patch

from carbon_elt.assets import (
    carbon_intensity_readings,
    generation_mix_readings,
    load_warehouse,
    regional_intensity_readings,
)
from carbon_elt.models import GenerationReading, IntensityReading, RegionalIntensityReading


def test_carbon_intensity_readings_asset() -> None:
    intensity_data = [
        IntensityReading(
            valid_from="2026-01-20T12:00Z",
            valid_to="2026-01-20T12:30Z",
            forecast=200,
            actual=187,
            index="moderate",
        )
    ]
    with patch("carbon_elt.assets.fetch_national_intensity", return_value=intensity_data):
        result = carbon_intensity_readings()
        assert len(result) == 1
        assert result[0].index == "moderate"


def test_generation_mix_readings_asset() -> None:
    generation_data = [
        GenerationReading(
            valid_from="2026-01-20T12:00Z",
            valid_to="2026-01-20T12:30Z",
            fuel_type="wind",
            percentage=35.7,
        )
    ]
    with patch("carbon_elt.assets.fetch_generation", return_value=generation_data):
        result = generation_mix_readings()
        assert len(result) == 1
        assert result[0].fuel_type == "wind"


def test_regional_intensity_readings_asset() -> None:
    regional_data = [
        RegionalIntensityReading(
            valid_from="2026-01-20T12:00Z",
            valid_to="2026-01-20T12:30Z",
            region_code="SE",
            forecast=210,
            actual=195,
            index="moderate",
        )
    ]
    with patch("carbon_elt.assets.fetch_regional_intensity", return_value=regional_data):
        result = regional_intensity_readings()
        assert len(result) == 1
        assert result[0].region_code == "SE"


def test_load_warehouse_asset() -> None:
    intensity_data = [
        IntensityReading(
            valid_from="2026-01-20T12:00Z",
            valid_to="2026-01-20T12:30Z",
            forecast=200,
            actual=187,
            index="moderate",
        )
    ]
    generation_data = [
        GenerationReading(
            valid_from="2026-01-20T12:00Z",
            valid_to="2026-01-20T12:30Z",
            fuel_type="wind",
            percentage=35.7,
        )
    ]
    regional_data = [
        RegionalIntensityReading(
            valid_from="2026-01-20T12:00Z",
            valid_to="2026-01-20T12:30Z",
            region_code="SE",
            forecast=210,
            actual=195,
            index="moderate",
        )
    ]
    mock_conn = MagicMock()
    with (
        patch("carbon_elt.assets.get_connection", return_value=mock_conn),
        patch("carbon_elt.assets.load_readings", return_value=1),
        patch("carbon_elt.assets.load_generation", return_value=1),
        patch("carbon_elt.assets.load_regional_intensity", return_value=1),
    ):
        result = load_warehouse(intensity_data, generation_data, regional_data)
        assert result["intensity"] == 1
        assert result["generation"] == 1
        assert result["regional"] == 1
        mock_conn.close.assert_called_once()
