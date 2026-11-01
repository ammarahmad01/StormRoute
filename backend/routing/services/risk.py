from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class RiskLevel(IntEnum):
    LOW = 0
    MODERATE = 1
    HIGH = 2
    SEVERE = 3
    NO_TRAVEL = 4


RISK_LABELS = {
    RiskLevel.LOW: "Low",
    RiskLevel.MODERATE: "Moderate",
    RiskLevel.HIGH: "High",
    RiskLevel.SEVERE: "Severe",
    RiskLevel.NO_TRAVEL: "No Travel",
}


def classify_wind(wind_mph: float) -> RiskLevel:
    if wind_mph < 25:
        return RiskLevel.LOW
    if wind_mph < 35:
        return RiskLevel.MODERATE
    if wind_mph < 45:
        return RiskLevel.HIGH
    if wind_mph < 55:
        return RiskLevel.SEVERE
    return RiskLevel.NO_TRAVEL


def classify_rain(rain_in_hr: float) -> RiskLevel:
    if rain_in_hr < 0.10:
        return RiskLevel.LOW
    if rain_in_hr < 0.25:
        return RiskLevel.MODERATE
    if rain_in_hr < 0.50:
        return RiskLevel.HIGH
    if rain_in_hr <= 1.00:
        return RiskLevel.SEVERE
    return RiskLevel.NO_TRAVEL


def classify_snow(snow_in_hr: float) -> RiskLevel:
    if snow_in_hr < 0.5:
        return RiskLevel.LOW
    if snow_in_hr < 1.0:
        return RiskLevel.MODERATE
    if snow_in_hr < 2.0:
        return RiskLevel.HIGH
    if snow_in_hr <= 3.0:
        return RiskLevel.SEVERE
    return RiskLevel.NO_TRAVEL


def apply_load_rules(wind_mph: float, load_lb: int, base_level: RiskLevel) -> tuple[RiskLevel, str | None]:
    if wind_mph >= 55:
        return max(base_level, RiskLevel.NO_TRAVEL), "wind_ge_55"
    if 45 <= wind_mph < 55 and load_lb > 30_000:
        return max(base_level, RiskLevel.NO_TRAVEL), "heavy_load_wind_45_54"
    if 35 <= wind_mph < 45 and load_lb > 40_000:
        return max(base_level, RiskLevel.SEVERE), "heavy_load_wind_35_44"
    return base_level, None


@dataclass(frozen=True)
class CheckpointRisk:
    wind: RiskLevel
    rain: RiskLevel
    snow: RiskLevel
    overall: RiskLevel
    dominant_factor: str | None
    load_rule_applied: str | None

    @property
    def score(self) -> int:
        return int(self.overall)


def overall_risk(wind_mph: float, rain_in_hr: float, snow_in_hr: float, load_lb: int) -> CheckpointRisk:
    wind_base = classify_wind(wind_mph)
    wind, load_rule = apply_load_rules(wind_mph, load_lb, wind_base)
    components = {"wind": wind, "rain": classify_rain(rain_in_hr), "snow": classify_snow(snow_in_hr)}
    overall = max(components.values())
    dominant = next((name for name, value in components.items() if value == overall), None)
    return CheckpointRisk(
        wind=wind,
        rain=components["rain"],
        snow=components["snow"],
        overall=overall,
        dominant_factor=dominant,
        load_rule_applied=load_rule,
    )

