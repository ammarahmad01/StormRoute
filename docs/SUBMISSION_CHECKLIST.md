# Submission Checklist

## Required deliverables
- [x] GitHub repository (public or access granted), link in README
- [x] Hosted application URL working
- [ ] Loom walkthrough, 5-10 minutes, link in README

## Functional requirements (from the brief)
- [x] Input: origin & destination, departure date/time, load weight
- [x] 3 route options generated through a routing API
- [x] Weather sampled every 10 / 25 / 50 miles
- [x] Weather taken at the **ETA** of each checkpoint
- [x] Risk calculated with the provided thresholds
- [x] Load rules applied (>=55 any; 45-54 & >30k; 35-44 & >40k)
- [x] Recommendation: Severe miles -> High miles -> average risk -> time
- [x] Map shows all routes, checkpoints, risk levels, ETAs, summaries
- [x] Visible weather heatmap along the corridor
- [x] 0-48 hour forecast slider

## Evaluation areas
**Routes, weather, risk & recommendation (40%)**
- [x] Unit tests for every threshold boundary and load rule
- [x] Ranking tests including ties and the heavy-load flip
- [x] ETA-based weather verified by hand on one trip

**UI, map & heatmap (40%)**
- [x] Smooth slider (no network on scrub)
- [x] Map responsive with long routes
- [x] Clear colours, legend, loading and error states
- [x] Works on mobile width

**Code quality (15%)**
- [x] Pure logic separated from I/O
- [x] Type hints / TypeScript types, consistent formatting, linting passes
- [x] No secrets committed, `.env.example` provided
- [ ] Meaningful commit history with multiple focused commits

**Documentation & walkthrough (5%)**
- [x] README: setup, env vars, architecture summary, assumptions
- [x] `docs/` folder complete and consistent with the code
- [ ] Loom covers demo, heavy-load scenario, heatmap, key code

## Final sanity run
- [ ] Fresh clone -> follow README -> app runs
- [x] `pytest` and `npm test` pass
- [ ] Hosted app tested in an incognito window
- [x] All placeholders replaced except the pending Loom URL
