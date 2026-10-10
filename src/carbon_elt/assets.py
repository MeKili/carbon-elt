"""Dagster assets for the carbon-elt ELT pipeline."""

from __future__ import annotations

import subprocess

from dagster import asset

from carbon_elt.config import get_settings
from carbon_elt.extract import (
    fetch_generation,
    fetch_national_intensity,
    fetch_regional_intensity,
)
from carbon_elt.models import GenerationReading, IntensityReading, RegionalIntensityReading
from carbon_elt.warehouse import (
    get_connection,
    init_schema,
    load_generation,
    load_readings,
    load_regional_intensity,
)


@asset
def carbon_intensity_readings() -> list[IntensityReading]:
    """Fetch current national carbon-intensity readings from the API."""
    return fetch_national_intensity()


@asset
def generation_mix_readings() -> list[GenerationReading]:
    """Fetch current generation mix data from the API."""
    return fetch_generation()


@asset
def regional_intensity_readings() -> list[RegionalIntensityReading]:
    """Fetch current regional carbon-intensity readings from the API."""
    return fetch_regional_intensity()


@asset
def load_warehouse(
    carbon_intensity_readings: list[IntensityReading],
    generation_mix_readings: list[GenerationReading],
    regional_intensity_readings: list[RegionalIntensityReading],
) -> dict[str, int]:
    """Load fetched data into DuckDB and return counts of rows loaded."""
    settings = get_settings()
    conn = get_connection(settings.duckdb_path)
    try:
        init_schema(conn)
        intensity_count = load_readings(conn, carbon_intensity_readings)
        generation_count = load_generation(conn, generation_mix_readings)
        regional_count = load_regional_intensity(conn, regional_intensity_readings)
        return {
            "intensity": intensity_count,
            "generation": generation_count,
            "regional": regional_count,
        }
    finally:
        conn.close()


@asset
def dbt_models(load_warehouse: dict[str, int]) -> dict[str, str]:
    """Run dbt models to transform raw data into staging and mart tables."""
    result = subprocess.run(
        ["dbt", "run"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"dbt run failed: {result.stderr}")
    return {"status": "success", "output": result.stdout}
