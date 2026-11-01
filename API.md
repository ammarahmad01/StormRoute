# API Reference

Base URL: `/api`. JSON in/out. All times are ISO-8601; the server converts to UTC.

## `GET /api/geocode?q=<text>`
Autocomplete for the origin/destination fields.

**200**
```json
{
  "results": [
    { "label": "Dallas, TX, USA", "lat": 32.7767, "lon": -96.797 }
  ]
}
```

## `POST /api/routes/analyze`

### Request
```json
{
  "origin":      { "label": "Dallas, TX", "lat": 32.7767, "lon": -96.797 },
  "destination": { "label": "Denver, CO", "lat": 39.7392, "lon": -104.9903 },
  "departure_time": "2026-11-02T08:00:00-06:00",
  "load_weight_lb": 42000,
  "sample_interval_miles": 25
}
```

### Validation
| Field | Rule |
|---|---|
| `origin`, `destination` | lat in [-90, 90], lon in [-180, 180]; must differ |
| `departure_time` | valid ISO datetime with offset; not more than ~15 days ahead (forecast limit) |
| `load_weight_lb` | integer, 0 to 80,000 |
| `sample_interval_miles` | one of `10`, `25`, `50` (default 25) |

### Response 200
```json
{
  "analysis_id": "3f1c...",
  "recommended_route_id": "route-2",
  "recommendation_reason": "Route 2 has 0 Severe miles (Route 1: 24, Route 3: 12) and takes 42 min longer than the fastest.",
  "warnings": [],
  "routes": [
    {
      "id": "route-2",
      "label": "Route 2",
      "distance_miles": 801.4,
      "duration_minutes": 760,
      "geometry": [[32.77, -96.79], [32.80, -96.80]],
      "summary": {
        "no_travel_miles": 0,
        "severe_miles": 0,
        "high_miles": 8.0,
        "moderate_miles": 120.5,
        "low_miles": 672.9,
        "average_risk": 0.41,
        "max_risk": "High",
        "blocked": false
      },
      "rank": 1,
      "checkpoints": [
        {
          "index": 0,
          "distance_miles": 0,
          "lat": 32.7767,
          "lon": -96.797,
          "eta": "2026-11-02T14:00:00Z",
          "segment_miles": 12.5,
          "weather": {
            "wind_mph": 14.2,
            "gust_mph": 22.0,
            "rain_in_hr": 0.0,
            "snow_in_hr": 0.0,
            "forecast_hour": "2026-11-02T14:00:00Z"
          },
          "risk": {
            "wind": "Low",
            "rain": "Low",
            "snow": "Low",
            "overall": "Low",
            "score": 0,
            "dominant_factor": null,
            "load_rule_applied": null
          }
        }
      ]
    }
  ]
}
```

`geometry` is decimated for display. Checkpoints are never decimated.

### Errors
| Status | Body | When |
|---|---|---|
| 400 | `{ "errors": { "field": ["msg"] } }` | Validation |
| 404 | `{ "detail": "No route found" }` | Provider returned nothing |
| 429 | `{ "detail": "Rate limited" }` | DRF throttle |
| 502 | `{ "detail": "Weather service unavailable" }` | Upstream failure after retry |

## `GET /api/analyses/{analysis_id}/heatmap`
All 49 hourly frames (hour 0 = departure hour) for the trip corridor.

```json
{
  "start_time": "2026-11-02T14:00:00Z",
  "hours": 48,
  "points": [[32.77, -96.79], [33.10, -97.20]],
  "frames": [
    [0, 1, 0],
    [0, 2, 1]
  ],
  "legend": ["Low", "Moderate", "High", "Severe", "No Travel"]
}
```

`frames[h][i]` is the risk score (0-4) for `points[i]` at hour `h`. Uses the same classifier and the same load weight as `/analyze`.

## `GET /api/health`
Returns `{ "status": "ok" }` for the host's health check.
