"""Command-line interface for carbon-elt pipeline and transforms."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from carbon_elt.config import get_settings
from carbon_elt.extract import fetch_generation, fetch_regional_intensity
from carbon_elt.pipeline import run
from carbon_elt.warehouse import (
    get_connection,
    init_schema,
    load_generation,
    load_regional_intensity,
)


def cmd_load(args: argparse.Namespace) -> int:
    """Load fresh data from the UK Carbon Intensity API into DuckDB."""
    counts = run()
    total = sum(counts.values())
    print(
        f"Loaded {counts['intensity']} intensity, {counts['generation']} generation, "
        f"and {counts['regional']} regional readings ({total} total) into DuckDB."
    )
    return 0


def cmd_load_generation(args: argparse.Namespace) -> int:
    """Load fresh generation mix data from the UK Carbon Intensity API into DuckDB."""
    settings = get_settings()
    readings = fetch_generation(settings)
    conn = get_connection(settings.duckdb_path)
    try:
        init_schema(conn)
        count = load_generation(conn, readings)
        print(f"Loaded {count} generation readings into DuckDB.")
        return 0
    finally:
        conn.close()


def cmd_load_regional(args: argparse.Namespace) -> int:
    """Load fresh regional carbon-intensity data from the UK Carbon Intensity API into DuckDB."""
    settings = get_settings()
    readings = fetch_regional_intensity(settings)
    conn = get_connection(settings.duckdb_path)
    try:
        init_schema(conn)
        count = load_regional_intensity(conn, readings)
        print(f"Loaded {count} regional readings into DuckDB.")
        return 0
    finally:
        conn.close()


def cmd_info(args: argparse.Namespace) -> int:
    """Show the current DuckDB warehouse path and configuration."""
    settings = get_settings()
    print(f"DuckDB warehouse: {settings.duckdb_path}")
    print(f"API base URL: {settings.carbon_api_base_url}")
    print(f"Request timeout: {settings.request_timeout_seconds}s")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show row counts and date ranges for all warehouse tables."""
    settings = get_settings()
    conn = get_connection(settings.duckdb_path)
    try:
        init_schema(conn)
        tables = [
            ("raw_national_intensity", "Intensity"),
            ("raw_generation", "Generation"),
            ("raw_regional_intensity", "Regional"),
        ]
        print("Warehouse status:")
        for table_name, label in tables:
            result = conn.execute(
                f"SELECT COUNT(*) as cnt, MIN(valid_from) as min_time, MAX(valid_to) as max_time "
                f"FROM {table_name}"
            ).fetchall()
            count, min_time, max_time = result[0]
            date_range = f"{min_time.date()} to {max_time.date()}" if min_time else "no data"
            print(f"  {label:15} {count:6} rows  ({date_range})")
        return 0
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the requested command."""
    parser = argparse.ArgumentParser(
        prog="carbon-elt",
        description="UK electricity-grid carbon-intensity ELT platform",
    )
    subparsers = parser.add_subparsers(dest="command", help="available commands")

    subparsers.add_parser("load", help="load intensity data from the API")
    subparsers.add_parser("load-generation", help="load generation-mix data from the API")
    subparsers.add_parser("load-regional", help="load regional carbon-intensity data from the API")
    subparsers.add_parser("info", help="show configuration and warehouse path")
    subparsers.add_parser("status", help="show warehouse table statistics")

    args = parser.parse_args(argv)

    commands: dict[str, Callable[[argparse.Namespace], int]] = {
        "load": cmd_load,
        "load-generation": cmd_load_generation,
        "load-regional": cmd_load_regional,
        "info": cmd_info,
        "status": cmd_status,
    }

    if not args.command:
        parser.print_help()
        return 0

    try:
        cmd = commands[args.command]
        return cmd(args)
    except KeyError:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
