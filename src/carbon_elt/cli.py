"""Command-line interface for carbon-elt pipeline and transforms."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from carbon_elt.config import get_settings
from carbon_elt.extract import fetch_generation
from carbon_elt.pipeline import run
from carbon_elt.warehouse import get_connection, init_schema, load_generation


def cmd_load(args: argparse.Namespace) -> int:
    """Load fresh data from the UK Carbon Intensity API into DuckDB."""
    count = run()
    print(f"Loaded {count} intensity readings into DuckDB.")
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


def cmd_info(args: argparse.Namespace) -> int:
    """Show the current DuckDB warehouse path and configuration."""
    settings = get_settings()
    print(f"DuckDB warehouse: {settings.duckdb_path}")
    print(f"API base URL: {settings.carbon_api_base_url}")
    print(f"Request timeout: {settings.request_timeout_seconds}s")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the requested command."""
    parser = argparse.ArgumentParser(
        prog="carbon-elt",
        description="UK electricity-grid carbon-intensity ELT platform",
    )
    subparsers = parser.add_subparsers(dest="command", help="available commands")

    subparsers.add_parser("load", help="load intensity data from the API")
    subparsers.add_parser("load-generation", help="load generation-mix data from the API")
    subparsers.add_parser("info", help="show configuration and warehouse status")

    args = parser.parse_args(argv)

    commands: dict[str, Callable[[argparse.Namespace], int]] = {
        "load": cmd_load,
        "load-generation": cmd_load_generation,
        "info": cmd_info,
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
