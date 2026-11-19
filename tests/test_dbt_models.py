"""Tests for dbt models and transformations."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from carbon_elt.models import IntensityReading
from carbon_elt.warehouse import RAW_TABLE, get_connection, init_schema, load_readings


def test_stg_national_intensity_deduplication() -> None:
    """Test that the staging model correctly deduplicates readings."""
    conn = get_connection(":memory:")
    init_schema(conn)

    base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    readings = [
        IntensityReading(
            valid_from=base_time,
            valid_to=base_time + timedelta(minutes=30),
            forecast=100,
            actual=105,
            index="low",
        ),
        IntensityReading(
            valid_from=base_time,
            valid_to=base_time + timedelta(minutes=30),
            forecast=100,
            actual=105,
            index="low",
        ),
        IntensityReading(
            valid_from=base_time + timedelta(minutes=30),
            valid_to=base_time + timedelta(minutes=60),
            forecast=110,
            actual=108,
            index="moderate",
        ),
    ]
    load_readings(conn, readings)

    result = conn.execute(f"SELECT COUNT(*) FROM {RAW_TABLE}").fetchone()
    assert result and result[0] == 3, "Raw table should have all 3 readings"

    stg_query = """
    with deduplicated as (
        select
            valid_from,
            valid_to,
            forecast,
            actual,
            index,
            row_number() over (partition by valid_from, valid_to order by valid_from) as dedup_rank
        from raw_national_intensity
    )
    select
        valid_from,
        valid_to,
        forecast,
        actual,
        index
    from deduplicated
    where dedup_rank = 1
    """
    stg_result = conn.execute(stg_query).fetchall()
    assert len(stg_result) == 2, "Staging view should have 2 deduplicated readings"

    conn.close()


def test_stg_national_intensity_preserves_data() -> None:
    """Test that staging model preserves all columns correctly."""
    conn = get_connection(":memory:")
    init_schema(conn)

    base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    readings = [
        IntensityReading(
            valid_from=base_time,
            valid_to=base_time + timedelta(minutes=30),
            forecast=150,
            actual=160,
            index="high",
        ),
    ]
    load_readings(conn, readings)

    stg_query = """
    with deduplicated as (
        select
            valid_from,
            valid_to,
            forecast,
            actual,
            index,
            row_number() over (partition by valid_from, valid_to order by valid_from) as dedup_rank
        from raw_national_intensity
    )
    select
        valid_from,
        valid_to,
        forecast,
        actual,
        index
    from deduplicated
    where dedup_rank = 1
    """
    result = conn.execute(stg_query).fetchone()
    assert result is not None
    assert result[2] == 150, "Forecast should be preserved"
    assert result[3] == 160, "Actual should be preserved"
    assert result[4] == "high", "Index should be preserved"

    conn.close()
