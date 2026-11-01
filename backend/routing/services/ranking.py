from __future__ import annotations

from dataclasses import dataclass

from .risk import RiskLevel


@dataclass(frozen=True)
class RiskPoint:
    level: RiskLevel
    miles: float
    forecast_available: bool = True


@dataclass(frozen=True)
class RouteSummary:
    no_travel_miles: float
    severe_miles: float
    high_miles: float
    moderate_miles: float
    low_miles: float
    average_risk: float
    max_risk: RiskLevel
    blocked: bool
    duration_minutes: float
    distance_miles: float


def summarize(points: list[RiskPoint], duration_minutes: float, distance_miles: float) -> RouteSummary:
    totals = {level: sum(point.miles for point in points if point.level == level) for level in RiskLevel}
    available = [point for point in points if point.forecast_available]
    available_miles = sum(point.miles for point in available)
    average = (
        sum(int(point.level) * point.miles for point in available) / available_miles
        if available_miles
        else 0.0
    )
    max_risk = max((point.level for point in points), default=RiskLevel.LOW)
    return RouteSummary(
        no_travel_miles=totals[RiskLevel.NO_TRAVEL],
        severe_miles=totals[RiskLevel.SEVERE],
        high_miles=totals[RiskLevel.HIGH],
        moderate_miles=totals[RiskLevel.MODERATE],
        low_miles=totals[RiskLevel.LOW],
        average_risk=average,
        max_risk=max_risk,
        blocked=totals[RiskLevel.NO_TRAVEL] > 0,
        duration_minutes=duration_minutes,
        distance_miles=distance_miles,
    )


def ranking_key(summary: RouteSummary) -> tuple[float, float, float, float, float]:
    return (
        round(summary.no_travel_miles, 1),
        round(summary.severe_miles, 1),
        round(summary.high_miles, 1),
        round(summary.average_risk, 2),
        round(summary.duration_minutes, 1),
    )


def rank_summaries(summaries: list[RouteSummary]) -> list[int]:
    return sorted(range(len(summaries)), key=lambda index: ranking_key(summaries[index]))

