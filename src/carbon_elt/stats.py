"""Warehouse statistics and data quality metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import duckdb


@dataclass
class TableStats:
    """Statistics for a single warehouse table."""

    table_name: str
    row_count: int
    min_date: datetime | None
    max_date: datetime | None

    @property
    def date_range_days(self) -> int | None:
        """Number of days covered by data in this table."""
        if self.min_date and self.max_date:
            return (self.max_date.date() - self.min_date.date()).days + 1
        return None


def get_table_stats(
    conn: duckdb.DuckDBPyConnection,
    table_name: str,
) -> TableStats:
    """Compute row count and date range for a warehouse table."""
    result = conn.execute(
        f"SELECT COUNT(*) as cnt, MIN(valid_from) as min_time, MAX(valid_to) as max_time "
        f"FROM {table_name}"
    ).fetchone()
    if result is None:
        raise RuntimeError(f"Failed to query {table_name}")
    count, min_time, max_time = result
    return TableStats(
        table_name=table_name,
        row_count=count or 0,
        min_date=min_time,
        max_date=max_time,
    )


def get_all_stats(conn: duckdb.DuckDBPyConnection) -> dict[str, TableStats]:
    """Compute statistics for all warehouse tables."""
    tables = ["raw_national_intensity", "raw_generation", "raw_regional_intensity"]
    return {table: get_table_stats(conn, table) for table in tables}


def get_intensity_index_distribution(conn: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Count intensity readings by index level."""
    rows = conn.execute(
        "SELECT index, COUNT(*) as cnt FROM raw_national_intensity GROUP BY index ORDER BY index"
    ).fetchall()
    distribution: dict[str, int] = {}
    for row in rows:
        distribution[row[0]] = row[1]
    return distribution


def get_latest_reading_time(conn: duckdb.DuckDBPyConnection, table_name: str) -> datetime | None:
    """Get the most recent reading timestamp from a table."""
    result = conn.execute(f"SELECT MAX(valid_to) FROM {table_name}").fetchone()
    return result[0] if result and result[0] else None
