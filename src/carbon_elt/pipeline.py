"""End-to-end ELT: fetch carbon-intensity data and load it into DuckDB."""

from __future__ import annotations

from carbon_elt.config import get_settings
from carbon_elt.extract import fetch_generation, fetch_national_intensity, fetch_regional_intensity
from carbon_elt.logging_config import get_logger
from carbon_elt.warehouse import (
    get_connection,
    init_schema,
    load_generation,
    load_readings,
    load_regional_intensity,
)

logger = get_logger(__name__)


def run() -> dict[str, int]:
    """Run the extract-load pipeline once; return counts of rows loaded."""
    logger.info("pipeline_start", event="Starting ELT pipeline run")
    settings = get_settings()

    logger.info("extracting_data", event="Extracting data from UK Carbon Intensity API")
    intensity_readings = fetch_national_intensity(settings)
    generation_readings = fetch_generation(settings)
    regional_readings = fetch_regional_intensity(settings)
    logger.info(
        "extract_complete",
        event="Data extraction complete",
        intensity_count=len(intensity_readings),
        generation_count=len(generation_readings),
        regional_count=len(regional_readings),
    )

    conn = get_connection(settings.duckdb_path)
    try:
        logger.info("initializing_schema", event="Initializing warehouse schema")
        init_schema(conn)

        logger.info("loading_data", event="Loading data into warehouse")
        intensity_count = load_readings(conn, intensity_readings)
        generation_count = load_generation(conn, generation_readings)
        regional_count = load_regional_intensity(conn, regional_readings)

        counts = {
            "intensity": intensity_count,
            "generation": generation_count,
            "regional": regional_count,
        }
        total = sum(counts.values())
        logger.info(
            "pipeline_complete",
            event="ELT pipeline completed successfully",
            total_rows_loaded=total,
            **counts,
        )
        return counts
    except Exception as e:
        logger.exception(
            "pipeline_error",
            event="ELT pipeline failed",
            error=str(e),
        )
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    counts = run()
    total = sum(counts.values())
    print(
        f"Loaded {counts['intensity']} intensity, {counts['generation']} "
        f"generation, and {counts['regional']} regional readings ({total} total) into DuckDB."
    )
