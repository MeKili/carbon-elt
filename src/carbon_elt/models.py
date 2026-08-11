"""Typed records for UK carbon-intensity data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class IntensityReading(BaseModel):
    """A national carbon-intensity reading for a single half-hour window."""

    valid_from: datetime
    valid_to: datetime
    forecast: int | None
    actual: int | None
    index: str
