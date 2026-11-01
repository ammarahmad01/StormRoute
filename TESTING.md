# Testing Strategy

Correctness of routes, weather, risk and ranking is 40% of the grade. Test it directly and visibly.

## 1. Backend unit tests (pytest)

### `test_risk.py`: the rules table
Parametrised boundary tests for each condition.

| Case | Input | Expected |
|---|---|---|
| Wind just below Moderate | 24.9 mph | Low |
| Wind at Moderate | 25 | Moderate |
| Wind gap value | 34.6 | Moderate |
| Wind at High | 35 | High |
| Wind at Severe | 45 | Severe |
| Wind at No Travel | 55 | No Travel |
| Rain at 0.10 / 0.25 / 0.50 | | Moderate / High / Severe |
| Rain at 1.00 | 1.00 | Severe |
| Rain above | 1.01 | No Travel |
| Snow at 0.5 / 1.0 / 2.0 | | Moderate / High / Severe |
| Snow at 3.0 | 3.0 | Severe |
| Snow above | 3.1 | No Travel |

### `test_load_rules.py`
| Wind | Load | Expected |
|---|---|---|
| 55 | 1,000 | No Travel |
| 60 | 80,000 | No Travel |
| 50 | 30,000 | Severe (not strictly >30k) |
| 50 | 30,001 | No Travel |
| 40 | 40,000 | High (not strictly >40k) |
| 40 | 40,001 | Severe |
| 30 | 80,000 | Moderate (rules don't apply) |
| 44.9 | 41,000 | Severe |
| Load rules never lower a level | rain Severe + wind High + 45k lb | Severe |

### `test_overall_risk.py`
Worst-of-three, `dominant_factor`, ties.

### `test_sampling.py`
- Checkpoints at multiples of interval plus the final point.
- Total of `segment_miles` equals route distance (within tolerance).
- ETA is monotonic and ends at departure + duration.
- Short route (< interval).
- Polyline with duplicate points.

### `test_ranking.py`
- Fewer Severe miles wins over everything else (even if slower).
- Tie on Severe -> fewer High miles.
- Tie on High -> lower average risk.
- Tie on average -> shorter time.
- No Travel route loses to any non-blocked route.
- All blocked -> still returns a rank order + warning.
- Rounding tolerance avoids false differences.
- **Scenario: a heavy load flips the recommendation** (same weather, 20k lb picks route A, 45k lb picks route B). Reuse this in the Loom.

### `test_weather_service.py`
Mock HTTP (`responses` / `requests-mock`):
- Picks the correct hourly index for an ETA.
- Batches all checkpoints into one request.
- Cache hit avoids a second request.
- Handles missing/null hourly values and upstream errors.

### `test_api.py`
- Valid request -> 200 with 3 routes, ranks 1..3, one recommended.
- Validation errors (interval not in 10/25/50, weight > 80k, past date).
- Provider/weather mocked; no network in CI.

## 2. Frontend tests (Vitest + Testing Library)
- Form validation and submit payload.
- Risk colour helper (`riskToColor`) for every level.
- Recommendation banner renders the reason and time penalty.
- Heatmap slider changes the frame without network calls (spy on `fetch`).

## 3. Manual QA checklist
- [ ] Short trip (~50 mi) and long trip (~1,500 mi).
- [ ] Interval 10 / 25 / 50 all work and change checkpoint count.
- [ ] Departure now vs. +36 h vs. +10 days.
- [ ] Load 10,000 vs. 45,000 lb on a windy day -> different outcome.
- [ ] Slider scrubs smoothly 0 -> 48; play button works.
- [ ] Mobile viewport.
- [ ] Slow network / provider failure -> readable error.
- [ ] No console errors.

## 4. Performance targets
- `/analyze` for ~1,000-mile trip at 25-mile interval: aim under ~5 s cold, under ~1 s warm cache.
- Heatmap frame switch: under one animation frame (16 ms) because data is in memory.
- Map stays responsive with 3 routes x ~100 checkpoints.

## 5. CI (optional, cheap win)
GitHub Actions: backend `pytest`, frontend `npm test && npm run build`, `ruff`/`black` and `eslint`/`prettier` checks.
