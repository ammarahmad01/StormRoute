# Submission Checklist

## Required deliverables
- [ ] GitHub repository (public or access granted), link in README
- [ ] Hosted application URL working
- [ ] Loom walkthrough, 5-10 minutes, link in README

## Functional requirements (from the brief)
- [ ] Input: origin & destination, departure date/time, load weight
- [ ] 3 route options generated through a routing API
- [ ] Weather sampled every 10 / 25 / 50 miles
- [ ] Weather taken at the **ETA** of each checkpoint
- [ ] Risk calculated with the provided thresholds
- [ ] Load rules applied (>=55 any; 45-54 & >30k; 35-44 & >40k)
- [ ] Recommendation: Severe miles -> High miles -> average risk -> time
- [ ] Map shows all routes, checkpoints, risk levels, ETAs, summaries
- [ ] Weather heatmap along the corridor
- [ ] 0-48 hour forecast slider

## Evaluation areas
**Routes, weather, risk & recommendation (40%)**
- [ ] Unit tests for every threshold boundary and load rule
- [ ] Ranking tests including ties and the heavy-load flip
- [ ] ETA-based weather verified by hand on one trip

**UI, map & heatmap (40%)**
- [ ] Smooth slider (no network on scrub)
- [ ] Map responsive with long routes
- [ ] Clear colours, legend, loading and error states
- [ ] Works on mobile width

**Code quality (15%)**
- [ ] Pure logic separated from I/O
- [ ] Type hints / TypeScript types, consistent formatting, linting passes
- [ ] No secrets committed, `.env.example` provided
- [ ] Meaningful commit history

**Documentation & walkthrough (5%)**
- [ ] README: setup, env vars, architecture summary, assumptions
- [ ] `docs/` folder complete and consistent with the code
- [ ] Loom covers demo, heavy-load scenario, heatmap, key code

## Final sanity run
- [ ] Fresh clone -> follow README -> app runs
- [ ] `pytest` and `npm test` pass
- [ ] Hosted app tested in an incognito window
- [ ] All placeholders (`<HOSTED_URL>`, `<LOOM_URL>`, `<GITHUB_URL>`) replaced
