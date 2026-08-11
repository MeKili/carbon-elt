"""carbon-elt — a local-first ELT platform for UK electricity-grid carbon-intensity data.

Pipeline: extract (Carbon Intensity API) -> load (DuckDB) -> transform (dbt) ->
orchestration (Dagster). This package currently implements the extract-load slice.
"""

__version__ = "0.1.0"
