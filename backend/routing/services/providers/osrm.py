from __future__ import annotations

import requests

from .base import Place, RouteOption


class OsrmProvider:
    base_url = "https://router.project-osrm.org"

    def __init__(self, timeout: float = 20):
        self.timeout = timeout

    def routes(self, origin: Place, destination: Place) -> list[RouteOption]:
        coordinates = f"{origin.lon},{origin.lat};{destination.lon},{destination.lat}"
        response = requests.get(
            f"{self.base_url}/route/v1/driving/{coordinates}",
            params={"overview": "full", "geometries": "geojson", "alternatives": "true"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            RouteOption(
                id=f"route-{index + 1}",
                label=f"Route {index + 1}",
                distance_miles=route["distance"] / 1609.344,
                duration_minutes=route["duration"] / 60,
                geometry=[(point[1], point[0]) for point in route["geometry"]["coordinates"]],
            )
            for index, route in enumerate(payload.get("routes", []))
        ]

    def route_via(self, origin: Place, waypoint: tuple[float, float], destination: Place, index: int) -> RouteOption | None:
        coordinates = f"{origin.lon},{origin.lat};{waypoint[1]},{waypoint[0]};{destination.lon},{destination.lat}"
        response = requests.get(
            f"{self.base_url}/route/v1/driving/{coordinates}",
            params={"overview": "full", "geometries": "geojson"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        route = response.json().get("routes", [None])[0]
        if not route:
            return None
        return RouteOption(
            id=f"route-{index}",
            label=f"Route {index}",
            distance_miles=route["distance"] / 1609.344,
            duration_minutes=route["duration"] / 60,
            geometry=[(point[1], point[0]) for point in route["geometry"]["coordinates"]],
        )

