"""End-to-end ELT: fetch carbon-intensity data and load it into DuckDB."""

from __future__ import annotations

from carbon_elt.config import get_settings
from carbon_elt.extract import fetch_generation, fetch_national_intensity
from carbon_elt.warehouse import (
    get_connection,
    init_schema,
    load_generation,
    load_readings,
)


def run() -> dict[str, int]:
    """Run the extract-load pipeline once; return counts of rows loaded."""
    settings = get_settings()
    intensity_readings = fetch_national_intensity(settings)
    generation_readings = fetch_generation(settings)
    conn = get_connection(settings.duckdb_path)
    try:
        init_schema(conn)
        intensity_count = load_readings(conn, intensity_readings)
        generation_count = load_generation(conn, generation_readings)
        return {"intensity": intensity_count, "generation": generation_count}
    finally:
        conn.close()


if __name__ == "__main__":
    counts = run()
    total = sum(counts.values())
    print(
        f"Loaded {counts['intensity']} intensity and {counts['generation']} "
        f"generation readings ({total} total) into DuckDB."
    )
