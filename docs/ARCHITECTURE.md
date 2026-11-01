# Architecture

## 1. High-level flow

```
React UI ──POST /api/routes/analyze──▶ Django
                                        │
          ┌─────────────────────────────┤
          ▼                             ▼
   Routing provider              Sampling + ETA
   (3 routes)                    (checkpoints every N miles)
                                        │
                                        ▼
                               Weather service (Open-Meteo)
                               batched, cached, hour of ETA
                                        │
                                        ▼
                               Risk classifier (+ load rules)
                                        │
                                        ▼
                               Ranking → recommended route
                                        │
React UI ◀───────────── JSON ───────────┘

React UI ──GET /api/analyses/{id}/heatmap──▶ 49 hourly frames (cached)
```

## 2. Backend modules

| Module | Responsibility | Pure? |
|---|---|---|
| `providers/base.py` | `RoutingProvider`, `GeocodingProvider` interfaces | - |
| `providers/mapbox.py` | Mapbox implementation | no (HTTP) |
| `providers/osrm.py` | Fallback implementation | no (HTTP) |
| `sampling.py` | Cumulative distance/time along polyline; checkpoint positions; ETAs | **yes** |
| `weather.py` | Batch request to Open-Meteo, pick hour per checkpoint, cache | no (HTTP) |
| `risk.py` | `classify_wind/rain/snow`, `apply_load_rules`, `overall_risk` | **yes** |
| `ranking.py` | Mile totals per level, average risk, sort key | **yes** |
| `heatmap.py` | Corridor grid, 49 frames of risk intensity | mostly |

Keep the **yes** modules free of I/O so they are trivially unit-testable. This is the 40% correctness area.

## 3. Data model (Django)

Minimal persistence, only what is needed to serve the heatmap and re-open results:

```
Analysis
  id (uuid), created_at
  origin_label, origin_lat, origin_lon
  dest_label, dest_lat, dest_lon
  departure_utc, load_weight_lb, interval_miles
  result_json (JSON)        # full analyze response
  heatmap_json (JSON, null) # lazily filled
```

No user accounts. Add a cleanup job or TTL if the DB grows.

## 4. Core algorithms

### 4.1 Checkpoint sampling
1. Decode polyline → list of `(lat, lon)`.
2. Compute cumulative distance (haversine) in miles.
3. Scale cumulative distance so the total equals the API's reported route distance (removes geometry vs. API drift).
4. Place checkpoints at `0, N, 2N, ...` and always include the **final point**.
5. Interpolate position between polyline vertices.

### 4.2 ETA
`eta(d) = departure + duration_total * (d / distance_total)`
Better: use per-step/leg `duration` from the routing response to build a cumulative duration curve and interpolate on it (highways vs. city speeds differ). Start with the proportional version, upgrade if time allows.

### 4.3 Weather lookup
- One Open-Meteo request per route with all checkpoint coordinates (comma-separated `latitude`/`longitude`), hourly variables, `timezone=GMT`, `wind_speed_unit=mph`, `precipitation_unit=inch`.
- For each checkpoint pick the hourly index nearest to its ETA (UTC).
- Cache key: `(round(lat,2), round(lon,2), hour_utc)`; TTL ~30-60 min.

### 4.4 Risk per checkpoint
See [RISK_AND_RANKING.md](RISK_AND_RANKING.md).

### 4.5 Route segments / miles
Each checkpoint represents `(d[i+1] - d[i-1]) / 2` miles (clamped at the ends). Sum miles by level per route.

### 4.6 Heatmap
- Build a corridor point set: sample every ~25 miles along all 3 routes (dedupe points within ~10 miles of each other).
- One batched Open-Meteo call for the corridor, hourly, 48 h.
- For each hour `h = 0..48` after departure compute risk intensity (0-4) per point using the same `risk.py` and load rules.
- Return compact arrays: `points: [[lat, lon], ...]`, `frames: [[0,1,0,2,...], ...]`.
- The frontend holds all 49 frames in memory, so slider movement triggers **no network calls**.

## 5. Frontend structure

```
src/
  api/client.ts            # fetch wrappers, typed
  types/api.ts             # response types
  components/
    TripForm.tsx
    RecommendationBanner.tsx
    RouteCard.tsx / RouteList.tsx
    CheckpointTable.tsx
    HeatmapControls.tsx    # slider, play/pause, legend
  map/
    MapView.tsx
    RouteLayer.tsx         # polyline colored per segment by risk
    CheckpointMarkers.tsx  # popups with ETA + weather + risk
    HeatLayer.tsx          # leaflet.heat, updates on frame change
  hooks/
    useAnalyze.ts  useHeatmap.ts  useDebouncedValue.ts
```

### Performance notes
- Colour polylines by splitting into risk-coloured segments, not one marker per vertex.
- Memoise layers; update the heat layer with `setLatLngs` instead of remounting.
- Debounce the slider (or use `requestAnimationFrame`) for smooth scrubbing.
- Decimate polylines (Douglas-Peucker) for display only.
- Lazy-load heatmap after the main results render.

## 6. Error handling

| Situation | Behaviour |
|---|---|
| Geocode finds nothing | 400 with field error; UI shows message |
| Fewer than 3 routes returned | Return what exists + `warnings: ["only N routes available"]` (see fallback in ASSUMPTIONS) |
| Weather API fails | Retry once; else 502 with clear message |
| ETA beyond forecast range | Checkpoint marked `forecast_unavailable`, excluded from averages, warning shown |
| Any checkpoint No Travel | Route flagged `blocked`; shown but never recommended unless all are blocked |

## 7. Security / ops
- API keys only on the backend.
- DRF throttling on `/analyze`.
- CORS restricted to the frontend origin.
- `DEBUG=0`, `SECRET_KEY` from env in production.
