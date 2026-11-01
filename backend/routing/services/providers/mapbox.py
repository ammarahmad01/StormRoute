from __future__ import annotations

import os

import requests

from .base import Place, RouteOption


class MapboxProvider:
    base_url = "https://api.mapbox.com"

    def __init__(self, token: str | None = None, timeout: float = 15):
        self.token = token or os.getenv("MAPBOX_TOKEN", "")
        self.timeout = timeout

    def _request(self, url: str, params: dict) -> dict:
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def routes(self, origin: Place, destination: Place) -> list[RouteOption]:
        if not self.token:
            return []
        coordinates = f"{origin.lon},{origin.lat};{destination.lon},{destination.lat}"
        payload = self._request(
            f"{self.base_url}/directions/v5/mapbox/driving/{coordinates}",
            {"alternatives": "true", "geometries": "geojson", "overview": "full", "access_token": self.token},
        )
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

    def search(self, query: str) -> list[Place]:
        if not self.token:
            return []
        payload = self._request(
            f"{self.base_url}/geocoding/v5/mapbox.places/{requests.utils.quote(query)}.json",
            {"access_token": self.token, "limit": 5, "types": "place,address,locality"},
        )
        return [
            Place(feature["place_name"], feature["center"][1], feature["center"][0])
            for feature in payload.get("features", [])
        ]

