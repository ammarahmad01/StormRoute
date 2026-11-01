# Weather-Aware Truck Routing

A React + Django web app that helps a truck driver choose the safest route based on **weather along the way**, **load weight**, and **travel time**.

> Live app: [https://storm-route-rho.vercel.app/](https://storm-route-rho.vercel.app/) · Walkthrough: pending · Repo: [github.com/ammarahmad01/StormRoute](https://github.com/ammarahmad01/StormRoute)

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
| Routing / geocoding | Mapbox Directions + Geocoding (pluggable provider, OSRM fallback) | Returns alternatives; see [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md) |
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
├── docs/                       # design, testing, deployment, and submission docs
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
- Full list in [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md).

## Documentation index

- [Architecture](docs/ARCHITECTURE.md)
- [Risk rules & ranking](docs/RISK_AND_RANKING.md)
- [API reference](docs/API.md)
- [Assumptions & edge cases](docs/ASSUMPTIONS.md)
- [Testing strategy](docs/TESTING.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md)

## Known limitations

See the bottom of [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md). Fill in honestly before submitting.

## Deployment

- Frontend: [storm-route-rho.vercel.app](https://storm-route-rho.vercel.app/)
- Backend health: [stormroute-6ted.onrender.com/api/health](https://stormroute-6ted.onrender.com/api/health)
- Repository: [github.com/ammarahmad01/StormRoute](https://github.com/ammarahmad01/StormRoute)
- Walkthrough: pending
