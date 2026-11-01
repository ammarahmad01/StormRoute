# Loom Walkthrough Script (target: 7-8 min, limit 5-10)

Prepare before recording: hosted app awake, two test trips ready, a windy scenario where load weight changes the recommendation, code editor open on `risk.py`, `ranking.py` and the tests.

## 0:00-0:45 Intro and problem
- "This is a weather-aware truck routing app: React + Django."
- Inputs: origin/destination, departure time, load weight. Output: three routes, ranked by weather risk, with a recommendation.

## 0:45-2:15 Live demo, light load
- Enter a long trip, pick the 25-mile interval, load 20,000 lb.
- Show the three routes on the map, the recommended one, the summary cards (distance, time, Severe/High miles, average risk).
- Click a checkpoint: ETA, forecast hour, wind/rain/snow, risk level and why.
- Point out the recommendation reason line and the time penalty versus the fastest route.

## 2:15-3:30 Live demo, heavy load
- Same trip, load 45,000 lb.
- Show how the same weather becomes **Severe/No Travel** under the load rules and the recommendation changes (or a route becomes blocked).
- Explain wind 35-44 mph + >40k lb -> Severe, 45-54 + >30k -> No Travel, >=55 always No Travel.

## 3:30-4:45 Heatmap
- Open the heatmap, scrub the 0-48 h slider, press play.
- State the difference: checkpoints use ETA weather; the heatmap shows the corridor at a chosen hour after departure.
- Mention that all 49 frames are loaded once, so scrubbing makes no network calls.

## 4:45-6:30 How it works (code)
- **Sampling + ETA** (`sampling.py`): checkpoints at the chosen interval, ETA from route duration.
- **Weather** (`weather.py`): one batched Open-Meteo request, hour nearest ETA, caching.
- **Risk** (`risk.py`): thresholds, boundary convention, load rules, worst-of-three.
- **Ranking** (`ranking.py`): tuple sort key: Severe miles, High miles, average risk, time. Mention the No Travel tier.

## 6:30-7:30 Tests and decisions
- Run `pytest`; show the boundary tests and the heavy-load flip scenario.
- Mention key assumptions: sustained wind, boundary rule, miles per checkpoint, 3-route fallback.

## 7:30-8:00 Wrap-up
- Limitations (no traffic/rest stops, forecast resolution).
- What you would do next (truck profile routing, gust toggle in UI, ETA by per-step speed).
- Thank them; show repo and README link.

## Recording tips
- 1080p, close unrelated tabs, zoom the browser to ~110%.
- Rehearse once; keep the code part short, since the grade is mostly logic and UI.
- Have a backup recording of the demo in case the free host is slow.
