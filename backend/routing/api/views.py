from __future__ import annotations

import math
import os
from datetime import datetime, timezone

import requests
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from routing.models import Analysis
from routing.services.providers.base import Place
from routing.services.providers.mapbox import MapboxProvider
from routing.services.providers.osrm import OsrmProvider
from routing.services.ranking import RiskPoint, rank_summaries, summarize
from routing.services.risk import RISK_LABELS, RiskLevel, overall_risk
from routing.services.sampling import sample_route
from routing.services.weather import OpenMeteoWeatherService

from .serializers import AnalyzeSerializer


class AnalyzeThrottle(SimpleRateThrottle):
    scope = "analyze"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


def _provider():
    return MapboxProvider() if os.getenv("MAPBOX_TOKEN") else OsrmProvider()


def _route_options(provider, origin, destination):
    options = provider.routes(origin, destination)
    if len(options) >= 3 or not options:
        return options
    fallback = OsrmProvider()
    lat_delta = destination.lat - origin.lat
    lon_delta = destination.lon - origin.lon
    length = math.hypot(lat_delta, lon_delta) or 1
    perpendicular = (-lon_delta / length, lat_delta / length)
    midpoint = ((origin.lat + destination.lat) / 2, (origin.lon + destination.lon) / 2)
    for offset in (-0.8, 0.8):
        if len(options) >= 3:
            break
        waypoint = (midpoint[0] + perpendicular[0] * offset, midpoint[1] + perpendicular[1] * offset)
        try:
            candidate = fallback.route_via(origin, waypoint, destination, len(options) + 1)
        except requests.RequestException:
            candidate = None
        if candidate and all(abs(candidate.distance_miles - existing.distance_miles) > 1 for existing in options):
            options.append(candidate)
    return options


def _display_geometry(geometry, max_points=500):
    if len(geometry) <= max_points:
        return geometry
    stride = max(1, len(geometry) // max_points)
    sampled = geometry[::stride]
    return sampled if sampled[-1] == geometry[-1] else sampled + [geometry[-1]]


def _iso(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _summary_from_payload(route):
    labels = {label: level for level, label in RISK_LABELS.items()}
    points = [
        RiskPoint(labels[checkpoint["risk"]["overall"]], checkpoint["segment_miles"])
        for checkpoint in route["checkpoints"]
        if checkpoint["risk"] is not None
    ]
    return summarize(points, route["duration_minutes"], route["distance_miles"])


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def geocode(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response({"results": []})
    try:
        results = _provider().search(query)
    except requests.RequestException:
        return Response({"detail": "Geocoding service unavailable"}, status=status.HTTP_502_BAD_GATEWAY)
    return Response({"results": [{"label": item.label, "lat": item.lat, "lon": item.lon} for item in results]})


@api_view(["POST"])
@throttle_classes([AnalyzeThrottle])
def analyze(request):
    serializer = AnalyzeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    values = serializer.validated_data
    departure = values["departure_time"]
    if departure.tzinfo is None:
        return Response({"errors": {"departure_time": ["An offset is required."]}}, status=400)
    departure = departure.astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    if departure < now:
        return Response({"errors": {"departure_time": ["Departure time cannot be in the past."]}}, status=400)
    if (departure - now).total_seconds() > 15 * 24 * 3600:
        return Response({"errors": {"departure_time": ["Departure time is beyond the forecast window."]}}, status=400)

    origin = Place(**values["origin"])
    destination = Place(**values["destination"])
    try:
        routes = _route_options(_provider(), origin, destination)
    except requests.RequestException:
        return Response({"detail": "Routing service unavailable"}, status=502)
    if not routes:
        return Response({"detail": "No route found"}, status=404)

    warnings = [] if len(routes) >= 3 else [f"only {len(routes)} routes available"]
    weather_service = OpenMeteoWeatherService()
    route_payloads = []
    try:
        for route in routes:
            checkpoints = sample_route(
                route.geometry,
                route.distance_miles,
                route.duration_minutes,
                values["sample_interval_miles"],
                departure,
            )
            forecasts = weather_service.forecast(checkpoints)
            checkpoint_payloads = []
            risk_points = []
            for checkpoint, weather in zip(checkpoints, forecasts):
                if weather.get("forecast_unavailable"):
                    warnings.append(f"{route.label} has unavailable forecast data")
                    checkpoint_payloads.append(
                        {
                            "index": checkpoint.index,
                            "distance_miles": checkpoint.distance_miles,
                            "lat": checkpoint.lat,
                            "lon": checkpoint.lon,
                            "eta": _iso(checkpoint.eta),
                            "segment_miles": checkpoint.segment_miles,
                            "weather": weather,
                            "risk": None,
                        }
                    )
                    continue
                risk = overall_risk(
                    weather["wind_mph"],
                    weather["rain_in_hr"],
                    weather["snow_in_hr"],
                    values["load_weight_lb"],
                )
                risk_points.append(RiskPoint(risk.overall, checkpoint.segment_miles))
                checkpoint_payloads.append(
                    {
                        "index": checkpoint.index,
                        "distance_miles": checkpoint.distance_miles,
                        "lat": checkpoint.lat,
                        "lon": checkpoint.lon,
                        "eta": _iso(checkpoint.eta),
                        "segment_miles": checkpoint.segment_miles,
                        "weather": weather,
                        "risk": {
                            "wind": RISK_LABELS[risk.wind],
                            "rain": RISK_LABELS[risk.rain],
                            "snow": RISK_LABELS[risk.snow],
                            "overall": RISK_LABELS[risk.overall],
                            "score": risk.score,
                            "dominant_factor": risk.dominant_factor,
                            "load_rule_applied": risk.load_rule_applied,
                        },
                    }
                )
            summary = summarize(risk_points, route.duration_minutes, route.distance_miles)
            route_payloads.append(
                {
                    "id": route.id,
                    "label": route.label,
                    "distance_miles": round(route.distance_miles, 1),
                    "duration_minutes": round(route.duration_minutes, 1),
                    "geometry": _display_geometry(route.geometry),
                    "summary": {
                        "no_travel_miles": round(summary.no_travel_miles, 1),
                        "severe_miles": round(summary.severe_miles, 1),
                        "high_miles": round(summary.high_miles, 1),
                        "moderate_miles": round(summary.moderate_miles, 1),
                        "low_miles": round(summary.low_miles, 1),
                        "average_risk": round(summary.average_risk, 2),
                        "max_risk": RISK_LABELS[summary.max_risk],
                        "blocked": summary.blocked,
                    },
                    "checkpoints": checkpoint_payloads,
                }
            )
    except requests.RequestException:
        return Response({"detail": "Weather service unavailable"}, status=502)

    summaries = [_summary_from_payload(route) for route in route_payloads]
    order = rank_summaries(summaries)
    for rank, index in enumerate(order, 1):
        route_payloads[index]["rank"] = rank
    recommended = route_payloads[order[0]]
    result = {
        "analysis_id": "",
        "recommended_route_id": recommended["id"],
        "recommendation_reason": f"{recommended['label']} is ranked first by the documented safety tuple.",
        "warnings": sorted(set(warnings)),
        "routes": sorted(route_payloads, key=lambda route: route["rank"]),
    }
    with transaction.atomic():
        analysis = Analysis.objects.create(
            origin_label=origin.label,
            origin_lat=origin.lat,
            origin_lon=origin.lon,
            dest_label=destination.label,
            dest_lat=destination.lat,
            dest_lon=destination.lon,
            departure_utc=departure,
            load_weight_lb=values["load_weight_lb"],
            interval_miles=values["sample_interval_miles"],
            result_json=result,
        )
        result["analysis_id"] = str(analysis.id)
        analysis.result_json = result
        analysis.save(update_fields=["result_json"])
    return Response(result)


@api_view(["GET"])
def heatmap(request, analysis_id):
    try:
        analysis = Analysis.objects.get(id=analysis_id)
    except (Analysis.DoesNotExist, ValueError):
        return Response({"detail": "Analysis not found"}, status=404)
    if analysis.heatmap_json is None:
        source_points = []
        for route in analysis.result_json.get("routes", []):
            source_points.extend((checkpoint["lat"], checkpoint["lon"]) for checkpoint in route.get("checkpoints", []))
        points = list(dict.fromkeys(source_points))
        if not points:
            analysis.heatmap_json = {"start_time": _iso(analysis.departure_utc), "hours": 48, "points": [], "frames": [[] for _ in range(49)], "legend": [RISK_LABELS[RiskLevel(level)] for level in range(5)]}
        else:
            try:
                forecasts = OpenMeteoWeatherService().hourly_forecast(points, analysis.departure_utc, 48)
            except requests.RequestException:
                return Response({"detail": "Weather service unavailable"}, status=502)
            frames = []
            for hour in range(49):
                frame = []
                for point_index in range(len(points)):
                    weather = forecasts[hour][point_index]
                    if weather.get("forecast_unavailable"):
                        frame.append(0)
                    else:
                        frame.append(int(overall_risk(weather["wind_mph"], weather["rain_in_hr"], weather["snow_in_hr"], analysis.load_weight_lb).overall))
                frames.append(frame)
            analysis.heatmap_json = {
                "start_time": _iso(analysis.departure_utc),
                "hours": 48,
                "points": points,
                "frames": frames,
                "legend": [RISK_LABELS[RiskLevel(level)] for level in range(5)],
            }
        analysis.save(update_fields=["heatmap_json"])
    return Response(analysis.heatmap_json)
