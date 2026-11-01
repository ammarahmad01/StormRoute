# Assumptions, Decisions & Edge Cases

Documenting ambiguity explicitly is part of "correctness and clarity". Update this file as you build.

## Ambiguities in the brief and how they are resolved

| # | Ambiguity | Decision | Rationale |
|---|---|---|---|
| 1 | "Sample weather every 10 / 25 / 50 miles" | User-selectable interval (default 25) | Most natural reading; lets the user trade detail for speed |
| 2 | Wind: sustained or gusts? | Sustained 10 m wind for classification; gusts shown in UI. Switchable via `WIND_METRIC=gust` | The 55 mph "No Travel" limit is closer to sustained-wind guidance; gusts would over-flag |
| 3 | Rain/snow units | Open-Meteo `rain + showers` and `snowfall` with `precipitation_unit=inch` -> in/hr (hourly value is the preceding hour's total) | Matches thresholds directly |
| 4 | Boundary values | Lower-bound inclusive; shared boundary goes to higher level; No Travel cut-off follows the brief's strict `>` | See RISK_AND_RANKING |
| 5 | Combining wind/rain/snow | Overall = worst of the three | Conservative and easy to explain |
| 6 | Load rules | Only raise the wind level; `>` strict on weight | Matches the wording |
| 7 | "Miles" at each level | Road length each checkpoint represents (half-gap to neighbours) | Needed to compute Severe/High miles |
| 8 | No Travel in ranking | Compared first (tier 0); all-blocked case warns the user | Brief is silent; recommending a No Travel route would be unsafe |
| 9 | "Balancing risk and time" | Strict lexicographic order from the brief; UI shows the time cost of the choice | The brief's order puts time last |
| 10 | Forecast slider vs. ETA weather | Two clearly labelled views: checkpoints use **ETA-time** weather; heatmap shows **hours after departure** | Avoid confusion |
| 11 | Heatmap intensity | Same classifier + same load weight as checkpoints | Consistent colours across views |
| 12 | Time zones | All internal times UTC; UI shows the browser's local time with the zone | Avoids DST bugs |

## Routing provider notes (verify before building)

- Requirement: **3 distinct route options**. Many routing APIs return fewer alternatives for some trips (especially long, mostly-single-corridor ones), and some free tiers cap alternatives by distance. Check your chosen provider's current limits first.
- Planned approach:
  1. Request alternatives from the provider.
  2. If fewer than 3 distinct routes come back, generate additional candidates by routing **via an offset waypoint** (a point roughly perpendicular to the straight line at ~40-60% of the trip) and keep results that differ materially (e.g. under ~70% geometry overlap).
  3. If still fewer than 3, return what exists with a `warnings` entry and explain it in the UI.
- Truck-specific profile (height, weight, hazmat avoidance) is a nice-to-have; passenger driving routes are acceptable if documented.

## Weather notes

- Open-Meteo forecasts reach about 16 days ahead; the brief's heatmap only needs 0-48 h.
- If a checkpoint's ETA is beyond available data, mark it `forecast_unavailable`, exclude it from averages, and warn.
- Past departure times: reject, or clamp to "now" with a warning.
- Hour selection: nearest hour to ETA (UTC).
- Spatial resolution: weather models are gridded; neighbouring checkpoints can return identical values. This is expected.

## Edge cases handled

- Origin equals destination (rejected).
- Very short trips (< interval): checkpoints at start and end only.
- Final checkpoint always included even if not a multiple of the interval.
- Load weight 0 and 80,000 lb.
- Same weather values exactly on thresholds (unit-tested).
- Routes that overlap heavily (deduplicated before ranking).
- Upstream timeouts (retry once, then clear error).
- Large trips (> 2,000 miles) with a 10-mile interval: cap checkpoints (e.g. max 300 per route) and warn, or auto-raise the interval.

## Out of scope (intentionally)

Auth/accounts, saved trips, hours-of-service planning, fuel/toll cost, road-surface/ice modelling, traffic. The brief says to prioritise correctness and clarity over extra features.

## Known limitations (fill in before submitting)

- [ ] Forecast accuracy depends on the Open-Meteo model resolution.
- [ ] ETA ignores traffic, rest stops and truck speed limits (unless you add them).
- [ ] Add anything you actually hit while building.
