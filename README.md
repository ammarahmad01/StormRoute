# Weather-Aware Truck Routing

A React + Django web app that helps a truck driver choose the safest route based on **weather along the way**, **load weight**, and **travel time**.

> Live app: `<HOSTED_URL>` · Walkthrough: `<LOOM_URL>` · Repo: `<GITHUB_URL>`

## What it does

1. Driver enters **origin, destination, departure date/time, load weight (lb)** and a **sampling interval** (10 / 25 / 50 miles).
2. Backend fetches **3 route options** from a routing API.
3. Each route is sampled into **checkpoints**; each checkpoint gets an **ETA**.
4. Weather is fetched **for each checkpoint's ETA** (not the departure time).
5. Each checkpoint is classified **Low / Moderate / High / Severe / No Travel** using the wind, rain and snow thresholds plus the **load rules**.
6. Routes are ranked by: fewest Severe miles → fewest High miles → lowest average risk → shortest time. The best is recommended.
7. The map shows all routes, checkpoints, risk, ETAs and summaries, plus a **weather heatmap** with a **0-48 hour slider**.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React + Vite + TypeScript, Leaflet (react-leaflet), leaflet.heat | Fast dev, simple map, canvas heatmap |
| Backend | Django + Django REST Framework | Required; clean API layer |
| Routing / geocoding | Mapbox Directions + Geocoding (pluggable provider, OSRM fallback) | Returns alternatives; see `docs/ASSUMPTIONS.md` |
| Weather | Open-Meteo (no key, hourly, mph + inch units, multi-location requests) | Free, batchable |
| Cache | Django cache (LocMem locally, Redis in prod optional) | Avoid duplicate weather calls |
| Tests | pytest + pytest-django, Vitest | Risk/ranking logic is the core of the grade |

## Repository layout

```
weather-truck-routing/
├── backend/
│   ├── manage.py
│   ├── config/                 # Django settings, urls
│   └── routing/
│       ├── api/                # serializers, views, urls
│       ├── services/
│       │   ├── providers/      # routing + geocoding adapters
│       │   ├── sampling.py     # checkpoints + ETA
│       │   ├── weather.py      # Open-Meteo client + batching + cache
│       │   ├── risk.py         # classification + load rules
│       │   ├── ranking.py      # route summary + ordering
│       │   └── heatmap.py      # corridor grid x 49 hours
│       └── tests/
├── frontend/
│   └── src/
│       ├── api/  components/  hooks/  map/  types/
├── *.md                        # design and submission docs (kept at repository root)
└── README.md
```

## Quick start

### Prerequisites
Python 3.11+, Node 20+, a Mapbox access token (free tier).

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill MAPBOX_TOKEN
python manage.py migrate
python manage.py runserver      # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev                     # http://localhost:5173
```

### Tests
```bash
cd backend && pytest
cd frontend && npm test
```

## Environment variables

| Variable | Where | Description |
|---|---|---|
| `MAPBOX_TOKEN` | backend | Routing + geocoding |
| `DJANGO_SECRET_KEY` | backend | Django secret |
| `DJANGO_DEBUG` | backend | `0` in production |
| `ALLOWED_HOSTS` | backend | Comma-separated |
| `CORS_ALLOWED_ORIGINS` | backend | Frontend origin(s) |
| `WIND_METRIC` | backend | `sustained` (default) or `gust` |
| `REDIS_URL` | backend | Optional cache |
| `VITE_API_BASE_URL` | frontend | Backend API base |

## Key decisions (short version)

- **Risk per checkpoint = worst of wind / rain / snow**, after load rules.
- **Ranking is lexicographic**, not a weighted score (exactly as the brief specifies).
- **"Miles" per risk level** = the road length each checkpoint represents.
- Full list in [`ASSUMPTIONS.md`](ASSUMPTIONS.md).

## Documentation index

- [Architecture](ARCHITECTURE.md)
- [Risk rules & ranking](RISK_AND_RANKING.md)
- [API reference](API.md)
- [Assumptions & edge cases](ASSUMPTIONS.md)
- [Testing strategy](TESTING.md)
- [Deployment](DEPLOYMENT.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Loom script](LOOM_SCRIPT.md)
- [Submission checklist](SUBMISSION_CHECKLIST.md)

## Known limitations

See the bottom of [`ASSUMPTIONS.md`](ASSUMPTIONS.md). Fill in honestly before submitting.
