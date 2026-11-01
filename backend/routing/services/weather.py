from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from django.core.cache import cache


class WeatherServiceError(Exception):
    pass


class OpenMeteoWeatherService:
    url = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout: float = 20):
        self.timeout = timeout

    def _fetch(self, coordinates: list[tuple[float, float]], start: datetime) -> dict[str, Any]:
        response = requests.get(
            self.url,
            params={
                "latitude": ",".join(f"{lat:.2f}" for lat, _ in coordinates),
                "longitude": ",".join(f"{lon:.2f}" for _, lon in coordinates),
                "hourly": "wind_speed_10m,wind_gusts_10m,rain,showers,snowfall",
                "forecast_days": 16,
                "timezone": "GMT",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def forecast(self, checkpoints: list[Any]) -> list[dict[str, Any]]:
        if not checkpoints:
            return []
        results: list[dict[str, Any] | None] = [None] * len(checkpoints)
        misses: list[int] = []
        for index, checkpoint in enumerate(checkpoints):
            hour = checkpoint.eta.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
            key = f"stormroute-weather:{round(checkpoint.lat, 2)}:{round(checkpoint.lon, 2)}:{hour.isoformat()}"
            cached = cache.get(key)
            if cached is None:
                misses.append(index)
            else:
                results[index] = cached
        if misses:
            payload = self._fetch([(checkpoints[i].lat, checkpoints[i].lon) for i in misses], checkpoints[misses[0]].eta)
            datasets = payload if isinstance(payload, list) else [payload]
            for local_index, checkpoint_index in enumerate(misses):
                data = datasets[min(local_index, len(datasets) - 1)]
                hourly = data.get("hourly", {})
                times = hourly.get("time", [])
                target = checkpoints[checkpoint_index].eta.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
                target_text = target.strftime("%Y-%m-%dT%H:%M")
                if target_text not in times:
                    results[checkpoint_index] = {"forecast_unavailable": True}
                    continue
                hour_index = times.index(target_text)
                wind = (hourly.get("wind_speed_10m") or [None])[hour_index]
                gust = (hourly.get("wind_gusts_10m") or [None])[hour_index]
                rain_values = hourly.get("rain") or [None]
                shower_values = hourly.get("showers") or [None]
                snow_values = hourly.get("snowfall") or [None]
                rain = rain_values[hour_index]
                showers = shower_values[hour_index]
                snow = snow_values[hour_index]
                if wind is None or rain is None or showers is None or snow is None:
                    results[checkpoint_index] = {"forecast_unavailable": True}
                    continue
                value = {
                    "wind_mph": wind,
                    "gust_mph": gust,
                    "rain_in_hr": rain + showers,
                    "snow_in_hr": snow,
                    "forecast_hour": target.isoformat().replace("+00:00", "Z"),
                }
                cache_key = f"stormroute-weather:{round(checkpoints[checkpoint_index].lat, 2)}:{round(checkpoints[checkpoint_index].lon, 2)}:{target.isoformat()}"
                cache.set(cache_key, value, 3600)
                results[checkpoint_index] = value
        return [result or {"forecast_unavailable": True} for result in results]

    def hourly_forecast(self, coordinates: list[tuple[float, float]], start: datetime, hours: int) -> list[list[dict[str, Any]]]:
        if not coordinates:
            return []
        payload = self._fetch(coordinates, start)
        datasets = payload if isinstance(payload, list) else [payload]
        frames: list[list[dict[str, Any]]] = []
        for hour in range(hours + 1):
            target = start.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
            target += timedelta(hours=hour)
            target_text = target.strftime("%Y-%m-%dT%H:%M")
            frame: list[dict[str, Any]] = []
            for data in datasets:
                hourly = data.get("hourly", {})
                times = hourly.get("time", [])
                if target_text not in times:
                    frame.append({"forecast_unavailable": True})
                    continue
                index = times.index(target_text)
                wind_values = hourly.get("wind_speed_10m") or []
                gust_values = hourly.get("wind_gusts_10m") or []
                rain_values = hourly.get("rain") or []
                shower_values = hourly.get("showers") or []
                snow_values = hourly.get("snowfall") or []
                if any(index >= len(values) for values in (wind_values, rain_values, shower_values, snow_values)):
                    frame.append({"forecast_unavailable": True})
                    continue
                frame.append({
                    "wind_mph": wind_values[index],
                    "gust_mph": gust_values[index] if index < len(gust_values) else None,
                    "rain_in_hr": rain_values[index] + shower_values[index],
                    "snow_in_hr": snow_values[index],
                    "forecast_hour": target.isoformat().replace("+00:00", "Z"),
                })
            frames.append(frame)
        return frames
