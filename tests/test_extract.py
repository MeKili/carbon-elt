"""Tests for parsing carbon-intensity API payloads (no network access)."""

from carbon_elt.extract import parse_intensity

SAMPLE_PAYLOAD = {
    "data": [
        {
            "from": "2026-01-20T12:00Z",
            "to": "2026-01-20T12:30Z",
            "intensity": {"forecast": 200, "actual": 187, "index": "moderate"},
        }
    ]
}


def test_parse_intensity_reads_a_row() -> None:
    readings = parse_intensity(SAMPLE_PAYLOAD)
    assert len(readings) == 1
    reading = readings[0]
    assert reading.forecast == 200
    assert reading.actual == 187
    assert reading.index == "moderate"


def test_parse_intensity_handles_empty_data() -> None:
    assert parse_intensity({"data": []}) == []
