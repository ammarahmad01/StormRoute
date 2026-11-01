import pytest

from routing.services.risk import (
    RiskLevel,
    classify_rain,
    classify_snow,
    classify_wind,
    overall_risk,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(24.9, RiskLevel.LOW), (25, RiskLevel.MODERATE), (34.6, RiskLevel.MODERATE), (35, RiskLevel.HIGH), (45, RiskLevel.SEVERE), (55, RiskLevel.NO_TRAVEL)],
)
def test_wind_boundaries(value, expected):
    assert classify_wind(value) == expected


@pytest.mark.parametrize(("value", "expected"), [(0.10, RiskLevel.MODERATE), (0.25, RiskLevel.HIGH), (0.50, RiskLevel.SEVERE), (1.00, RiskLevel.SEVERE), (1.01, RiskLevel.NO_TRAVEL)])
def test_rain_boundaries(value, expected):
    assert classify_rain(value) == expected


@pytest.mark.parametrize(("value", "expected"), [(0.5, RiskLevel.MODERATE), (1.0, RiskLevel.HIGH), (2.0, RiskLevel.SEVERE), (3.0, RiskLevel.SEVERE), (3.1, RiskLevel.NO_TRAVEL)])
def test_snow_boundaries(value, expected):
    assert classify_snow(value) == expected


def test_load_rule_and_worst_factor():
    risk = overall_risk(40, 0, 0, 40_001)
    assert risk.wind == RiskLevel.SEVERE
    assert risk.overall == RiskLevel.SEVERE
    assert risk.load_rule_applied == "heavy_load_wind_35_44"

    rain_dominates = overall_risk(10, 0.60, 0.2, 20_000)
    assert rain_dominates.overall == RiskLevel.SEVERE
    assert rain_dominates.dominant_factor == "rain"

