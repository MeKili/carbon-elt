"""Typed records for UK carbon-intensity data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class IntensityReading(BaseModel):
    """A national carbon-intensity reading for a single half-hour window."""

    valid_from: datetime = Field(..., description="Start of the half-hour window (UTC)")
    valid_to: datetime = Field(..., description="End of the half-hour window (UTC)")
    forecast: int | None = Field(None, description="Forecast carbon intensity (gCO₂/kWh)")
    actual: int | None = Field(None, description="Actual carbon intensity (gCO₂/kWh)")
    index: str = Field(..., description="Index category (very low, low, moderate, high, very high)")


class GenerationReading(BaseModel):
    """Generation mix data for a single half-hour window."""

    valid_from: datetime = Field(..., description="Start of the half-hour window (UTC)")
    valid_to: datetime = Field(..., description="End of the half-hour window (UTC)")
    fuel_type: str = Field(..., description="Fuel source type (e.g. wind, gas, coal, nuclear)")
    percentage: float = Field(..., description="Percentage of grid supply from this fuel type")


class RegionalIntensityReading(BaseModel):
    """Regional carbon-intensity reading for a single half-hour window."""

    valid_from: datetime = Field(..., description="Start of the half-hour window (UTC)")
    valid_to: datetime = Field(..., description="End of the half-hour window (UTC)")
    region_code: str = Field(..., description="Regional identifier (e.g. N, E, SE)")
    forecast: int | None = Field(None, description="Forecast carbon intensity (gCO₂/kWh)")
    actual: int | None = Field(None, description="Actual carbon intensity (gCO₂/kWh)")
    index: str = Field(..., description="Index category (very low, low, moderate, high, very high)")
