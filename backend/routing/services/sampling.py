from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt


EARTH_RADIUS_MILES = 3958.7613


@dataclass(frozen=True)
class Checkpoint:
    index: int
    distance_miles: float
    lat: float
    lon: float
    segment_miles: float
    eta: datetime


def haversine_miles(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(radians, a)
    lat2, lon2 = map(radians, b)
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    value = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(value))


def _interpolate(points: list[tuple[float, float]], cumulative: list[float], distance: float) -> tuple[float, float]:
    if distance <= 0:
        return points[0]
    if distance >= cumulative[-1]:
        return points[-1]
    for index in range(1, len(points)):
        if cumulative[index] >= distance:
            gap = cumulative[index] - cumulative[index - 1]
            fraction = 0 if gap == 0 else (distance - cumulative[index - 1]) / gap
            return (
                points[index - 1][0] + (points[index][0] - points[index - 1][0]) * fraction,
                points[index - 1][1] + (points[index][1] - points[index - 1][1]) * fraction,
            )
    return points[-1]


def sample_route(
    geometry: list[tuple[float, float]],
    distance_miles: float,
    duration_minutes: float,
    interval_miles: int,
    departure: datetime,
) -> list[Checkpoint]:
    if len(geometry) < 2:
        raise ValueError("A route must contain at least two geometry points")
    if distance_miles <= 0 or duration_minutes < 0:
        raise ValueError("Route distance must be positive and duration cannot be negative")
    raw_gaps = [haversine_miles(geometry[i - 1], geometry[i]) for i in range(1, len(geometry))]
    raw_total = sum(raw_gaps)
    if raw_total == 0:
        raise ValueError("Route geometry must span a positive distance")
    cumulative = [0.0]
    for gap in raw_gaps:
        cumulative.append(cumulative[-1] + gap)
    scale = distance_miles / raw_total
    scaled = [value * scale for value in cumulative]
    distances = list(range(0, int(distance_miles), interval_miles))
    if not distances or distances[-1] != distance_miles:
        distances.append(distance_miles)
    checkpoints: list[Checkpoint] = []
    for index, distance in enumerate(distances):
        lat, lon = _interpolate(geometry, scaled, float(distance))
        if index == 0:
            segment = (distances[1] - distances[0]) / 2
        elif index == len(distances) - 1:
            segment = (distances[-1] - distances[-2]) / 2
        else:
            segment = (distances[index + 1] - distances[index - 1]) / 2
        eta = departure + timedelta(minutes=duration_minutes * distance / distance_miles)
        checkpoints.append(Checkpoint(index, float(distance), lat, lon, segment, eta))
    return checkpoints

