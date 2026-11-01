from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from rest_framework.test import APIClient

from routing.services.providers.base import RouteOption


def _route(route_id, offset):
    return RouteOption(
        id=route_id,
        label=f"Route {route_id}",
        distance_miles=100 + offset,
        duration_minutes=120 + offset,
        geometry=[(32.0, -96.0), (33.0 + offset / 100, -95.0)],
    )


class FakeProvider:
    def routes(self, origin, destination):
        return [_route("1", 0), _route("2", 10), _route("3", 20)]


class FakeWeather:
    def forecast(self, checkpoints):
        return [
            {
                "wind_mph": 20,
                "gust_mph": 25,
                "rain_in_hr": 0,
                "snow_in_hr": 0,
                "forecast_hour": checkpoint.eta.isoformat(),
            }
            for checkpoint in checkpoints
        ]


def test_analyze_returns_ranked_routes_and_checkpoints(db):
    payload = {
        "origin": {"label": "Dallas", "lat": 32.7767, "lon": -96.797},
        "destination": {"label": "Denver", "lat": 39.7392, "lon": -104.9903},
        "departure_time": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
        "load_weight_lb": 20_000,
        "sample_interval_miles": 25,
    }
    with patch("routing.api.views._provider", return_value=FakeProvider()), patch(
        "routing.api.views.OpenMeteoWeatherService", return_value=FakeWeather()
    ):
        response = APIClient().post("/api/routes/analyze", payload, format="json")

    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 3
    assert [route["rank"] for route in data["routes"]] == [1, 2, 3]
    assert data["recommended_route_id"] == data["routes"][0]["id"]
