"""Tests for warehouse statistics and data quality metrics."""

from datetime import datetime

from carbon_elt.models import IntensityReading
from carbon_elt.stats import (
    get_all_stats,
    get_intensity_index_distribution,
    get_latest_reading_time,
    get_table_stats,
)
from carbon_elt.warehouse import get_connection, init_schema, load_readings


def test_get_table_stats_empty_table() -> None:
    """Get stats for an empty table returns zeros and None dates."""
    conn = get_connection(":memory:")
    init_schema(conn)

    stats = get_table_stats(conn, "raw_national_intensity")

    assert stats.table_name == "raw_national_intensity"
    assert stats.row_count == 0
    assert stats.min_date is None
    assert stats.max_date is None
    assert stats.date_range_days is None
    conn.close()


def test_get_table_stats_with_data() -> None:
    """Get stats for a populated table returns correct values."""
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
            valid_from=datetime(2026, 1, 21, 12, 0),
            valid_to=datetime(2026, 1, 21, 12, 30),
            forecast=210,
            actual=195,
            index="high",
        ),
    ]
    load_readings(conn, readings)

    stats = get_table_stats(conn, "raw_national_intensity")

    assert stats.row_count == 2
    assert stats.min_date == datetime(2026, 1, 20, 12, 0)
    assert stats.max_date == datetime(2026, 1, 21, 12, 30)
    assert stats.date_range_days == 2
    conn.close()


def test_get_all_stats() -> None:
    """Get stats for all warehouse tables."""
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
    load_readings(conn, readings)

    all_stats = get_all_stats(conn)

    assert "raw_national_intensity" in all_stats
    assert "raw_generation" in all_stats
    assert "raw_regional_intensity" in all_stats
    assert all_stats["raw_national_intensity"].row_count == 1
    assert all_stats["raw_generation"].row_count == 0
    assert all_stats["raw_regional_intensity"].row_count == 0
    conn.close()


def test_get_intensity_index_distribution() -> None:
    """Count intensity readings by index level."""
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
            index="high",
        ),
        IntensityReading(
            valid_from=datetime(2026, 1, 20, 13, 0),
            valid_to=datetime(2026, 1, 20, 13, 30),
            forecast=220,
            actual=205,
            index="moderate",
        ),
    ]
    load_readings(conn, readings)

    distribution = get_intensity_index_distribution(conn)

    assert distribution["moderate"] == 2
    assert distribution["high"] == 1
    conn.close()


def test_get_latest_reading_time() -> None:
    """Get the most recent reading timestamp from a table."""
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
            valid_from=datetime(2026, 1, 21, 12, 0),
            valid_to=datetime(2026, 1, 21, 12, 30),
            forecast=210,
            actual=195,
            index="high",
        ),
    ]
    load_readings(conn, readings)

    latest = get_latest_reading_time(conn, "raw_national_intensity")

    assert latest == datetime(2026, 1, 21, 12, 30)
    conn.close()


def test_get_latest_reading_time_empty_table() -> None:
    """Get latest reading from an empty table returns None."""
    conn = get_connection(":memory:")
    init_schema(conn)

    latest = get_latest_reading_time(conn, "raw_national_intensity")

    assert latest is None
    conn.close()
