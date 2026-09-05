"""Tests for the DuckDB warehouse layer (in-memory, no files)."""

from datetime import datetime

from carbon_elt.models import GenerationReading, IntensityReading
from carbon_elt.warehouse import (
    RAW_GENERATION_TABLE,
    RAW_TABLE,
    get_connection,
    init_schema,
    load_generation,
    load_readings,
)


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


def test_daily_index_share_calculation() -> None:
    conn = get_connection(":memory:")
    init_schema(conn)
    readings = [
        IntensityReading(
            valid_from=datetime(2026, 1, 20, 12, 0),
            valid_to=datetime(2026, 1, 20, 12, 30),
            forecast=200,
            actual=187,
            index="moderate",
        ),
        IntensityReading(
            valid_from=datetime(2026, 1, 20, 12, 30),
            valid_to=datetime(2026, 1, 20, 13, 0),
            forecast=210,
            actual=195,
            index="moderate",
        ),
        IntensityReading(
            valid_from=datetime(2026, 1, 20, 13, 0),
            valid_to=datetime(2026, 1, 20, 13, 30),
            forecast=220,
            actual=205,
            index="high",
        ),
        IntensityReading(
            valid_from=datetime(2026, 1, 20, 13, 30),
            valid_to=datetime(2026, 1, 20, 14, 0),
            forecast=230,
            actual=215,
            index="high",
        ),
    ]
    inserted = load_readings(conn, readings)
    assert inserted == 4

    result = conn.execute(
        """
        select index, count(*) as cnt
        from raw_national_intensity
        where date(valid_from) = '2026-01-20'
        group by index
        order by index
        """
    ).fetchall()
    assert result is not None
    assert len(result) == 2
    assert result[0] == ("high", 2)
    assert result[1] == ("moderate", 2)
    conn.close()


def test_load_generation_inserts_rows() -> None:
    conn = get_connection(":memory:")
    init_schema(conn)
    readings = [
        GenerationReading(
            valid_from=datetime(2026, 1, 20, 12, 0),
            valid_to=datetime(2026, 1, 20, 12, 30),
            fuel_type="wind",
            percentage=45.5,
        ),
        GenerationReading(
            valid_from=datetime(2026, 1, 20, 12, 0),
            valid_to=datetime(2026, 1, 20, 12, 30),
            fuel_type="gas",
            percentage=30.2,
        ),
    ]
    inserted = load_generation(conn, readings)
    assert inserted == 2

    result = conn.execute(f"SELECT COUNT(*) FROM {RAW_GENERATION_TABLE}").fetchone()
    assert result is not None
    assert result[0] == 2

    result = conn.execute(
        f"SELECT fuel_type, percentage FROM {RAW_GENERATION_TABLE} WHERE fuel_type = 'wind'"
    ).fetchone()
    assert result is not None
    assert result[0] == "wind"
    assert result[1] == 45.5
    conn.close()
