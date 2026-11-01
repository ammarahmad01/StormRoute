from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Place:
    label: str
    lat: float
    lon: float


@dataclass(frozen=True)
class RouteOption:
    id: str
    label: str
    distance_miles: float
    duration_minutes: float
    geometry: list[tuple[float, float]]


class RoutingProvider(Protocol):
    def routes(self, origin: Place, destination: Place) -> list[RouteOption]:
        ...


class GeocodingProvider(Protocol):
    def search(self, query: str) -> list[Place]:
        ...

