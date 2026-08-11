"""DuckDB warehouse: connection, schema and loading of raw readings."""

from __future__ import annotations

import duckdb

from carbon_elt.models import IntensityReading

RAW_TABLE = "raw_national_intensity"


def get_connection(path: str = ":memory:") -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection at the given path (defaults to in-memory)."""
    return duckdb.connect(path)


def init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the raw readings table if it does not already exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {RAW_TABLE} (
            valid_from TIMESTAMP,
            valid_to   TIMESTAMP,
            forecast   INTEGER,
            actual     INTEGER,
            index      VARCHAR
        )
        """
    )


def load_readings(conn: duckdb.DuckDBPyConnection, readings: list[IntensityReading]) -> int:
    """Insert readings into the raw table and return the number of rows inserted."""
    rows = [(r.valid_from, r.valid_to, r.forecast, r.actual, r.index) for r in readings]
    conn.executemany(
        f"INSERT INTO {RAW_TABLE} (valid_from, valid_to, forecast, actual, index) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    return len(rows)
