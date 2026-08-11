"""Tests for the DuckDB warehouse layer (in-memory, no files)."""

from datetime import datetime

from carbon_elt.models import IntensityReading
from carbon_elt.warehouse import RAW_TABLE, get_connection, init_schema, load_readings


def test_load_readings_inserts_rows() -> None:
    conn = get_connection(":memory:")
    init_schema(conn)
    readings = [
        IntensityReading(
            valid_from=datetime(2026, 1, 20, 12, 0),
            valid_to=datetime(2026, 1, 20, 12, 30),
            forecast=200,
            actual=187,
            index="moderate",
        )
    ]
    inserted = load_readings(conn, readings)
    assert inserted == 1

    result = conn.execute(f"SELECT COUNT(*) FROM {RAW_TABLE}").fetchone()
    assert result is not None
    assert result[0] == 1
    conn.close()
