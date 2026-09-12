"""Dagster assets for the carbon-elt ELT pipeline."""

from __future__ import annotations

from dagster import asset

from carbon_elt.config import get_settings
from carbon_elt.extract import fetch_generation, fetch_national_intensity
from carbon_elt.models import GenerationReading, IntensityReading
from carbon_elt.warehouse import get_connection, init_schema, load_generation, load_readings


@asset
def carbon_intensity_readings() -> list[IntensityReading]:
    """Fetch current national carbon-intensity readings from the API."""
    return fetch_national_intensity()


@asset
def generation_mix_readings() -> list[GenerationReading]:
    """Fetch current generation mix data from the API."""
    return fetch_generation()


@asset
def load_warehouse(
    carbon_intensity_readings: list[IntensityReading],
    generation_mix_readings: list[GenerationReading],
) -> dict[str, int]:
    """Load fetched data into DuckDB and return counts of rows loaded."""
    settings = get_settings()
    conn = get_connection(settings.duckdb_path)
    try:
        init_schema(conn)
        intensity_count = load_readings(conn, carbon_intensity_readings)
        generation_count = load_generation(conn, generation_mix_readings)
        return {"intensity": intensity_count, "generation": generation_count}
    finally:
        conn.close()
