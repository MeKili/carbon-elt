# carbon-elt

A local-first ELT platform for UK electricity-grid carbon-intensity data. Fetches real-time generation mix, regional, and national carbon-intensity readings from the [UK Carbon Intensity API](https://carbonintensity.org), loads them into DuckDB, and transforms them into analytics-ready marts with dbt and Dagster orchestration.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv).

```bash
git clone https://github.com/mekili/carbon-elt.git
cd carbon-elt
uv sync
```

Create `.env` to override defaults (optional):

```bash
cp .env.example .env
```

## Usage

### CLI Commands

```bash
# Load all data (intensity, generation, regional) from the API
uv run carbon-elt load

# Load only generation mix data
uv run carbon-elt load-generation

# Load only regional carbon-intensity data
uv run carbon-elt load-regional

# Show warehouse configuration
uv run carbon-elt info

# Show table statistics (row counts and date ranges)
uv run carbon-elt status
```

### dbt

Transform raw data into staging and analytics marts:

```bash
# Run all models
dbt run

# Run data quality tests
dbt test

# Run specific model
dbt run -s stg_national_intensity
dbt run -s mart_daily_intensity
```

### Dagster

Start the Dagster UI to orchestrate the pipeline:

```bash
dagster dev
```

Access at `http://localhost:3000` to view assets, runs, and logs.

## Architecture

**Raw tables** (loaded from API):
- `raw_national_intensity` — National carbon-intensity readings
- `raw_generation` — Generation mix by fuel type
- `raw_regional_intensity` — Regional carbon-intensity readings

**Staging models** (dbt):
- `stg_national_intensity` — Cleaned national readings
- `stg_generation` — Cleaned generation mix
- `stg_regional_intensity` — Cleaned regional readings

**Mart models** (dbt):
- `mart_daily_intensity` — Daily average national intensity
- `mart_daily_index_share` — Daily % time at each intensity index level
- `mart_daily_generation_mix` — Daily average generation mix by fuel type
- `mart_regional_daily_intensity` — Daily average regional intensity by region

**Orchestration** (Dagster):
- Assets fetch data from the API and load into DuckDB
- Dependencies ensure staging models run before marts
- Runs are idempotent (upsert on time-window)

## Testing

Run all tests:

```bash
uv run pytest
```

Run linting, formatting, and type checking:

```bash
uv run ruff format .
uv run ruff check . --fix
uv run mypy src
```

## Project Structure

```
.
├── src/carbon_elt/          # Python package
│   ├── cli.py               # CLI commands (load, info, status)
│   ├── config.py            # Settings and configuration
│   ├── extract.py           # API fetching and parsing
│   ├── models.py            # Pydantic data models
│   ├── warehouse.py         # DuckDB schema and loading
│   ├── assets.py            # Dagster assets
│   └── pipeline.py          # End-to-end ELT run
├── models/                  # dbt models
│   ├── stg_*.sql            # Staging models
│   ├── mart_*.sql           # Mart (analytics) models
│   └── schema.yml           # dbt source/model definitions and tests
├── macros/                  # dbt macros (generic tests)
├── tests/                   # pytest test suite
└── dbt_project.yml          # dbt configuration
```

## Data

UK Carbon Intensity API endpoint: `https://api.carbonintensity.org.uk`

- **Intensity** (`/intensity`) — Forecasted and actual carbon intensity (g CO₂/kWh), updated half-hourly
- **Generation** (`/generation`) — % generation mix by fuel type, updated half-hourly
- **Regional** (`/regional`) — Regional intensity by UK region code, updated half-hourly

## Development

The pipeline handles idempotent, incremental loads: loading the same time-window multiple times replaces previous records, preventing duplicates.

All Python code is type-checked with mypy (strict mode), formatted with ruff, linted with ruff, and tested with pytest. dbt models include data quality tests (timestamps, valid index values, percentage ranges).
