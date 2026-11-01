# Deployment

A hosted app is a required deliverable. Keep it simple and reliable.

## Recommended setup

| Part | Host | Notes |
|---|---|---|
| Backend (Django) | Render / Railway / Fly.io | Free or hobby tier is fine |
| Frontend (React) | Vercel / Netlify | Static build |
| Database | SQLite for demo, or the host's Postgres | Only stores analyses |
| Cache | Local-memory cache, or host Redis | Optional |

Alternative: serve the built React app from Django with WhiteNoise (one service, no CORS). Easiest to host if you only want one URL.

## Backend (Render example)

1. Add to `backend/requirements.txt`: `gunicorn`, `whitenoise`, `dj-database-url`, `django-cors-headers`, `psycopg[binary]` (if Postgres).
2. Settings:
   - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` from env.
   - `CORS_ALLOWED_ORIGINS` includes the frontend URL.
   - `STATIC_ROOT` + WhiteNoise middleware.
3. Render web service:
   - Root directory: `backend`
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
   - Health check path: `/api/health`
4. Env vars: `MAPBOX_TOKEN`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.

## Frontend (Vercel example)

1. Root directory: `frontend`, framework preset: Vite.
2. Env var: `VITE_API_BASE_URL=https://<your-backend>/api`.
3. Build: `npm run build`, output: `dist`.

## Free-tier gotchas

- Free web services may **sleep** and take ~30-60 s to wake. Open the app a minute before the demo or recording, and mention this in the README.
- Restrict the Mapbox token to your domains (URL restrictions) if it ever reaches the browser; keep it server-side only.
- Use a different SECRET_KEY in production.

## Pre-submission verification

- [ ] Hosted URL loads without console errors.
- [ ] A fresh analysis from the hosted URL works end-to-end.
- [ ] Heatmap loads and the slider works on the hosted version.
- [ ] CORS is correct (no blocked requests in the network tab).
- [ ] README has the hosted URL.
- [ ] Repo is public (or access is granted to reviewers) and contains no secrets (`.env` in `.gitignore`).
