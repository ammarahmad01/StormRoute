# Risk Rules & Route Ranking

This is the most heavily graded part (40% with routes/weather). Everything here is implemented in pure functions with unit tests.

## 1. Levels

| Level | Numeric score |
|---|---|
| Low | 0 |
| Moderate | 1 |
| High | 2 |
| Severe | 3 |
| No Travel | 4 |

## 2. Threshold table (from the brief)

| Condition | Low | Moderate | High | Severe | No Travel |
|---|---|---|---|---|---|
| Wind (mph) | <25 | 25-34 | 35-44 | 45-54 | >=55 |
| Rain (in/hr) | <0.10 | 0.10-0.25 | 0.25-0.50 | 0.50-1.00 | >1.00 |
| Snow (in/hr) | <0.5 | 0.5-1.0 | 1.0-2.0 | 2.0-3.0 | >3.0 |

### Boundary convention (documented decision)
The table has shared boundaries (e.g. 0.25 belongs to both Moderate and High) and gaps (34 to 35 mph). The app uses **continuous thresholds, lower bound inclusive**:

- Wind: `<25` Low, `<35` Moderate, `<45` High, `<55` Severe, else No Travel.
- Rain: `<0.10` Low, `<0.25` Moderate, `<0.50` High, `<=1.00` Severe, `>1.00` No Travel.
- Snow: `<0.5` Low, `<1.0` Moderate, `<2.0` High, `<=3.0` Severe, `>3.0` No Travel.

Rule: a value exactly on a shared boundary takes the **higher** level (conservative), except at the No Travel cut-off, where the brief's strict `>` is followed literally (rain 1.00 = Severe, snow 3.0 = Severe). Wind 34.6 mph is Moderate (<35), which handles the gap between "34" and "35".

## 3. Load rules (override wind)

| Wind | Load | Result |
|---|---|---|
| >=55 mph | any | No Travel |
| 45-54 mph | > 30,000 lb | No Travel |
| 35-44 mph | > 40,000 lb | Severe |

Applied **after** the base wind classification, and only ever **raise** the level:

```python
def apply_load_rules(wind_mph, load_lb, base_level):
    if wind_mph >= 55:
        return NO_TRAVEL
    if 45 <= wind_mph < 55 and load_lb > 30_000:
        return max(base_level, NO_TRAVEL)
    if 35 <= wind_mph < 45 and load_lb > 40_000:
        return max(base_level, SEVERE)
    return base_level
```

Note `>` is strict: exactly 30,000 lb or 40,000 lb does **not** trigger the rule.

## 4. Overall checkpoint risk

```
overall = max(wind_level_after_load_rules, rain_level, snow_level)
```

The response also keeps each component and a `dominant_factor` (`wind` / `rain` / `snow`) so the UI can explain *why* a checkpoint is risky.

### Worked examples

| Wind | Rain | Snow | Load | Wind level | Overall |
|---|---|---|---|---|---|
| 20 | 0.00 | 0.0 | 45,000 | Low | Low |
| 38 | 0.00 | 0.0 | 35,000 | High | High |
| 38 | 0.00 | 0.0 | 45,000 | Severe (load rule) | Severe |
| 48 | 0.05 | 0.0 | 28,000 | Severe | Severe |
| 48 | 0.05 | 0.0 | 32,000 | No Travel (load rule) | No Travel |
| 56 | 0.00 | 0.0 | 5,000 | No Travel | No Travel |
| 10 | 0.60 | 0.2 | 20,000 | Low | Severe (rain) |
| 10 | 0.05 | 1.5 | 20,000 | Low | High (snow) |

## 5. Route summary metrics

Each checkpoint represents a stretch of road. For checkpoint `i` at distance `d[i]`:

```
miles[i] = (d[i+1] - d[i-1]) / 2     # first/last: half-gap to the neighbour
```
(Sum of all `miles[i]` equals route length.)

Per route compute:

- `no_travel_miles`, `severe_miles`, `high_miles`, `moderate_miles`, `low_miles`
- `average_risk` = mile-weighted mean of numeric scores
- `max_risk` = worst level on the route
- `duration_minutes`, `distance_miles`
- `blocked` = `no_travel_miles > 0`

Checkpoints whose forecast is unavailable are excluded from `average_risk` and surfaced as a warning.

## 6. Ranking (lexicographic)

The brief gives a strict priority order, so use a tuple sort key, **not** a weighted score:

```python
key = (
    route.no_travel_miles,   # tier 0: my addition, see below
    route.severe_miles,      # 1
    route.high_miles,        # 2
    route.average_risk,      # 3
    route.duration_minutes,  # 4
)
best = min(routes, key=key)
```

### Tier 0 (No Travel) - documented addition
The brief lists Severe first but never says what to do with No Travel. Recommending a route with a No Travel stretch would be wrong, so No Travel miles are compared first. If *every* route has No Travel, the least-bad one is still ranked first but the UI shows a prominent **"No safe route at this departure time"** warning and suggests a different departure time.

### Float tolerance
Compare miles and average risk after rounding (e.g. 1 decimal for miles, 2 for average) so floating-point noise does not decide between "equal" routes. Equal values fall through to the next criterion.

### "Balancing risk and travel time"
The brief says "balancing", but its priority list makes time the last tie-breaker. The UI therefore also shows the time cost of the recommendation: *"+42 min vs. fastest route, avoids 31 Severe miles."* This makes the balance visible without changing the specified ordering.

## 7. Recommendation explanation

Generate a short human-readable reason, e.g.:

> Route B recommended: 0 Severe miles (A: 24, C: 12), 8 High miles. Takes 42 min longer than the fastest route.

Build it from the first criterion where the winner differs from the runner-up.
