"""Extract national carbon-intensity and generation data from the UK Carbon Intensity API."""

from __future__ import annotations

from typing import Any

import httpx

from carbon_elt.config import Settings, get_settings
from carbon_elt.models import GenerationReading, IntensityReading


def parse_intensity(payload: dict[str, Any]) -> list[IntensityReading]:
    """Parse the ``/intensity`` JSON payload into typed readings."""
    readings: list[IntensityReading] = []
    for row in payload.get("data", []):
        intensity = row.get("intensity", {})
        readings.append(
            IntensityReading(
                valid_from=row["from"],
                valid_to=row["to"],
                forecast=intensity.get("forecast"),
                actual=intensity.get("actual"),
                index=intensity.get("index", "unknown"),
            )
        )
    return readings


def fetch_national_intensity(settings: Settings | None = None) -> list[IntensityReading]:
    """Fetch the current national carbon-intensity readings from the API."""
    settings = settings or get_settings()
    url = f"{settings.carbon_api_base_url}/intensity"
    response = httpx.get(url, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return parse_intensity(response.json())


def parse_generation(payload: dict[str, Any]) -> list[GenerationReading]:
    """Parse the ``/generation`` JSON payload into typed readings."""
    readings: list[GenerationReading] = []
    for row in payload.get("data", []):
        valid_from = row["from"]
        valid_to = row["to"]
        for fuel_type, percentage in row.get("generationmix", []):
            readings.append(
                GenerationReading(
                    valid_from=valid_from,
                    valid_to=valid_to,
                    fuel_type=fuel_type,
                    percentage=percentage,
                )
            )
    return readings


def fetch_generation(settings: Settings | None = None) -> list[GenerationReading]:
    """Fetch the current generation mix from the API."""
    settings = settings or get_settings()
    url = f"{settings.carbon_api_base_url}/generation"
    response = httpx.get(url, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return parse_generation(response.json())
