"""Tests for parsing carbon-intensity API payloads (no network access)."""

from carbon_elt.extract import parse_generation, parse_intensity

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


SAMPLE_GENERATION_PAYLOAD = {
    "data": [
        {
            "from": "2026-01-20T12:00Z",
            "to": "2026-01-20T12:30Z",
            "generationmix": [
                ("coal", 5.2),
                ("gas", 38.1),
                ("wind", 35.7),
                ("nuclear", 16.4),
                ("other", 4.6),
            ],
        }
    ]
}


def test_parse_generation_reads_fuel_types() -> None:
    readings = parse_generation(SAMPLE_GENERATION_PAYLOAD)
    assert len(readings) == 5
    fuels = {r.fuel_type: r.percentage for r in readings}
    assert fuels["coal"] == 5.2
    assert fuels["gas"] == 38.1
    assert fuels["wind"] == 35.7
    assert fuels["nuclear"] == 16.4
    assert fuels["other"] == 4.6


def test_parse_generation_handles_empty_data() -> None:
    assert parse_generation({"data": []}) == []
