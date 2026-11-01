# Implementation Plan

Ordered to protect the 40% correctness section first, then the 40% UI/map section.

## Phase 0: Setup (about 1 h)
- [ ] Repo, `.gitignore`, `.env.example`, backend + frontend scaffolds.
- [ ] Pick routing provider, get tokens, make one successful manual call to routing + Open-Meteo.
- [ ] Verify you can really get 3 routes for a long test trip (Dallas -> Denver, Chicago -> Atlanta).

## Phase 1: Core logic, pure functions (about 3-4 h)
- [ ] `risk.py` + tests (thresholds, boundaries, load rules, worst-of-three).
- [ ] `sampling.py` + tests (checkpoints, ETAs, segment miles).
- [ ] `ranking.py` + tests (summaries, lexicographic key, tier 0, rounding).
- [ ] Heavy-load flip scenario test.

## Phase 2: Integrations (about 3 h)
- [ ] Provider interface + Mapbox adapter (+ OSRM fallback if needed).
- [ ] Geocoding endpoint.
- [ ] Fallback to generate a 3rd route via waypoint if provider returns fewer.
- [ ] Open-Meteo batching + hourly pick + cache + tests with mocks.

## Phase 3: API (about 2 h)
- [ ] `POST /api/routes/analyze` with serializers + validation.
- [ ] `Analysis` model and migration.
- [ ] `GET /api/analyses/{id}/heatmap`.
- [ ] Error handling, throttling, health endpoint.

## Phase 4: Frontend (about 6-8 h)
- [ ] Trip form (autocomplete, datetime, weight, interval).
- [ ] Map with 3 route polylines, selection, recommended highlight.
- [ ] Risk-coloured route segments, checkpoint markers + popups (ETA, weather, risk).
- [ ] Route summary cards (distance, time, Severe/High miles, average risk, rank).
- [ ] Recommendation banner with reason and time penalty.
- [ ] Heatmap layer + 0-48 h slider + play button + legend.
- [ ] Loading, empty and error states; responsive layout.

## Phase 5: Polish & performance (about 2-3 h)
- [ ] Decimate display geometry, memoise layers, update heat layer in place.
- [ ] Prefetch heatmap after results render.
- [ ] Lighthouse / manual smoothness pass with long routes.
- [ ] Lint/format, remove dead code, tidy commits.

## Phase 6: Docs, deploy, Loom (about 2-3 h)
- [ ] Finish README, ASSUMPTIONS limitations.
- [ ] Deploy backend + frontend; verify on hosted URL.
- [ ] Rehearse and record the product walkthrough.
- [ ] Complete the final submission review.

## Priorities if time is short

1. Correct risk + load rules + ranking (with tests).
2. ETA-based weather per checkpoint.
3. Map with routes, checkpoints, recommendation.
4. Heatmap + slider, smooth.
5. Everything else.

Do **not** spend time on auth, saved trips, or extras: the brief explicitly says correctness and clarity first.

## Suggested commit history

Small, meaningful commits show how you work:
`feat(risk): classify wind/rain/snow`, `feat(risk): load rules`, `test(ranking): heavy-load flip`, `feat(api): analyze endpoint`, `feat(ui): route layer`, `feat(ui): heatmap slider`, `docs: README + assumptions`.
