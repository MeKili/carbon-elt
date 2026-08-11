"""End-to-end ELT: fetch national carbon-intensity data and load it into DuckDB."""

from __future__ import annotations

from carbon_elt.config import get_settings
from carbon_elt.extract import fetch_national_intensity
from carbon_elt.warehouse import get_connection, init_schema, load_readings


def run() -> int:
    """Run the extract-load pipeline once; return the number of rows loaded."""
    settings = get_settings()
    readings = fetch_national_intensity(settings)
    conn = get_connection(settings.duckdb_path)
    try:
        init_schema(conn)
        return load_readings(conn, readings)
    finally:
        conn.close()


if __name__ == "__main__":
    count = run()
    print(f"Loaded {count} readings into DuckDB.")
