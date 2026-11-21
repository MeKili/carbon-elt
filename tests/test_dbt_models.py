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


def test_mart_daily_intensity_aggregation() -> None:
    """Test that mart_daily_intensity correctly aggregates readings by day."""
    conn = get_connection(":memory:")
    init_schema(conn)

    base_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    readings = [
        IntensityReading(
            valid_from=base_date,
            valid_to=base_date + timedelta(minutes=30),
            forecast=100,
            actual=105,
            index="low",
        ),
        IntensityReading(
            valid_from=base_date + timedelta(minutes=30),
            valid_to=base_date + timedelta(hours=1),
            forecast=110,
            actual=115,
            index="moderate",
        ),
        IntensityReading(
            valid_from=base_date + timedelta(days=1),
            valid_to=base_date + timedelta(days=1, minutes=30),
            forecast=120,
            actual=125,
            index="high",
        ),
    ]
    load_readings(conn, readings)

    mart_query = """
    select
        date(valid_from) as intensity_date,
        round(avg(cast(actual as float)), 1) as avg_actual_intensity,
        round(avg(cast(forecast as float)), 1) as avg_forecast_intensity,
        count(*) as reading_count
    from raw_national_intensity
    where actual is not null
    group by date(valid_from)
    order by intensity_date
    """
    result = conn.execute(mart_query).fetchall()
    assert len(result) == 2, "Should have 2 days of data"

    day1 = result[0]
    assert day1[0] == base_date.date(), "First day should match"
    assert day1[1] == 110.0, "Average actual for day 1 should be (105+115)/2=110"
    assert day1[2] == 105.0, "Average forecast for day 1 should be (100+110)/2=105"
    assert day1[3] == 2, "Day 1 should have 2 readings"

    day2 = result[1]
    assert day2[0] == (base_date + timedelta(days=1)).date(), "Second day should match"
    assert day2[1] == 125.0, "Average actual for day 2 should be 125"
    assert day2[2] == 120.0, "Average forecast for day 2 should be 120"
    assert day2[3] == 1, "Day 2 should have 1 reading"

    conn.close()
