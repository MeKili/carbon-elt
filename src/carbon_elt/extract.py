"""Extract national carbon-intensity and generation data from the UK Carbon Intensity API."""

from __future__ import annotations

import time
from typing import Any

import httpx

from carbon_elt.config import Settings, get_settings
from carbon_elt.models import GenerationReading, IntensityReading, RegionalIntensityReading


def _fetch_with_retry(url: str, timeout: float, max_retries: int = 3) -> httpx.Response:
    """Fetch a URL with exponential backoff retry on transient errors."""
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = httpx.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2**attempt
                time.sleep(wait_time)
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    time.sleep(wait_time)
            else:
                raise
    raise last_error or RuntimeError("Fetch failed after all retries")


def parse_intensity(payload: dict[str, Any]) -> list[IntensityReading]:
    """Parse the ``/intensity`` JSON payload into typed readings."""
    readings: list[IntensityReading] = []
    for i, row in enumerate(payload.get("data", [])):
        try:
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
        except KeyError as e:
            raise ValueError(f"Missing required field {e} in intensity data at index {i}") from e
    return readings


def fetch_national_intensity(settings: Settings | None = None) -> list[IntensityReading]:
    """Fetch the current national carbon-intensity readings from the API."""
    settings = settings or get_settings()
    url = f"{settings.carbon_api_base_url}/intensity"
    response = _fetch_with_retry(url, settings.request_timeout_seconds)
    return parse_intensity(response.json())


def parse_generation(payload: dict[str, Any]) -> list[GenerationReading]:
    """Parse the ``/generation`` JSON payload into typed readings."""
    readings: list[GenerationReading] = []
    for i, row in enumerate(payload.get("data", [])):
        try:
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
        except KeyError as e:
            raise ValueError(f"Missing required field {e} in generation data at index {i}") from e
    return readings


def fetch_generation(settings: Settings | None = None) -> list[GenerationReading]:
    """Fetch the current generation mix from the API."""
    settings = settings or get_settings()
    url = f"{settings.carbon_api_base_url}/generation"
    response = _fetch_with_retry(url, settings.request_timeout_seconds)
    return parse_generation(response.json())


def parse_regional_intensity(payload: dict[str, Any]) -> list[RegionalIntensityReading]:
    """Parse the ``/regional`` JSON payload into typed readings."""
    readings: list[RegionalIntensityReading] = []
    for i, row in enumerate(payload.get("data", [])):
        try:
            intensity = row.get("intensity", {})
            readings.append(
                RegionalIntensityReading(
                    valid_from=row["from"],
                    valid_to=row["to"],
                    region_code=row["regionid"],
                    forecast=intensity.get("forecast"),
                    actual=intensity.get("actual"),
                    index=intensity.get("index", "unknown"),
                )
            )
        except KeyError as e:
            raise ValueError(f"Missing required field {e} in regional data at index {i}") from e
    return readings


def fetch_regional_intensity(settings: Settings | None = None) -> list[RegionalIntensityReading]:
    """Fetch regional carbon-intensity readings from the API."""
    settings = settings or get_settings()
    url = f"{settings.carbon_api_base_url}/regional"
    response = _fetch_with_retry(url, settings.request_timeout_seconds)
    return parse_regional_intensity(response.json())
