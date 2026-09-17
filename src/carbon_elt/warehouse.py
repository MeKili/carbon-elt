"""DuckDB warehouse: connection, schema and loading of raw readings."""

from __future__ import annotations

import duckdb

from carbon_elt.models import GenerationReading, IntensityReading, RegionalIntensityReading

RAW_TABLE = "raw_national_intensity"
RAW_GENERATION_TABLE = "raw_generation"
RAW_REGIONAL_TABLE = "raw_regional_intensity"


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
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {RAW_REGIONAL_TABLE} (
            valid_from TIMESTAMP,
            valid_to   TIMESTAMP,
            region_code VARCHAR,
            forecast   INTEGER,
            actual     INTEGER,
            index      VARCHAR
        )
        """
    )


def load_readings(conn: duckdb.DuckDBPyConnection, readings: list[IntensityReading]) -> int:
    """Load intensity readings, replacing any existing records with the same time window."""
    if not readings:
        return 0
    rows = [(r.valid_from, r.valid_to, r.forecast, r.actual, r.index) for r in readings]
    time_windows = [(r[0], r[1]) for r in rows]
    for valid_from, valid_to in time_windows:
        conn.execute(
            f"DELETE FROM {RAW_TABLE} WHERE valid_from = ? AND valid_to = ?",
            [valid_from, valid_to],
        )
    conn.executemany(
        f"INSERT INTO {RAW_TABLE} (valid_from, valid_to, forecast, actual, index) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    return len(rows)


def load_generation(conn: duckdb.DuckDBPyConnection, readings: list[GenerationReading]) -> int:
    """Load generation readings, replacing any existing records with the same time window."""
    if not readings:
        return 0
    rows = [(r.valid_from, r.valid_to, r.fuel_type, r.percentage) for r in readings]
    time_windows = set((r[0], r[1]) for r in rows)
    for valid_from, valid_to in time_windows:
        conn.execute(
            f"DELETE FROM {RAW_GENERATION_TABLE} WHERE valid_from = ? AND valid_to = ?",
            [valid_from, valid_to],
        )
    conn.executemany(
        f"INSERT INTO {RAW_GENERATION_TABLE} (valid_from, valid_to, fuel_type, percentage) "
        "VALUES (?, ?, ?, ?)",
        rows,
    )
    return len(rows)


def load_regional_intensity(
    conn: duckdb.DuckDBPyConnection,
    readings: list[RegionalIntensityReading],
) -> int:
    """Load regional intensity readings, replacing any existing records with same time window."""
    if not readings:
        return 0
    rows = [
        (r.valid_from, r.valid_to, r.region_code, r.forecast, r.actual, r.index) for r in readings
    ]
    time_windows = set((r[0], r[1]) for r in rows)
    for valid_from, valid_to in time_windows:
        conn.execute(
            f"DELETE FROM {RAW_REGIONAL_TABLE} WHERE valid_from = ? AND valid_to = ?",
            [valid_from, valid_to],
        )
    conn.executemany(
        f"INSERT INTO {RAW_REGIONAL_TABLE} "
        "(valid_from, valid_to, region_code, forecast, actual, index) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    return len(rows)
