"""DuckDB warehouse: connection, schema and loading of raw readings."""

from __future__ import annotations

import duckdb

from carbon_elt.models import GenerationReading, IntensityReading

RAW_TABLE = "raw_national_intensity"
RAW_GENERATION_TABLE = "raw_generation"


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
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {RAW_GENERATION_TABLE} (
            valid_from TIMESTAMP,
            valid_to   TIMESTAMP,
            fuel_type  VARCHAR,
            percentage DOUBLE
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


def load_generation(conn: duckdb.DuckDBPyConnection, readings: list[GenerationReading]) -> int:
    """Insert generation readings into the raw table and return the number of rows inserted."""
    rows = [(r.valid_from, r.valid_to, r.fuel_type, r.percentage) for r in readings]
    conn.executemany(
        f"INSERT INTO {RAW_GENERATION_TABLE} (valid_from, valid_to, fuel_type, percentage) "
        "VALUES (?, ?, ?, ?)",
        rows,
    )
    return len(rows)
