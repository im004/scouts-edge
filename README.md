# The Scout's Edge

The Scout's Edge is a deployed full-stack football analytics and tournament simulation platform. It pairs a FastAPI backend with a PostgreSQL database hosted on Neon, a Next.js/TypeScript frontend hosted on Vercel, and a Docker-based local development workflow. The backend is deployed on Render, GitHub Actions runs automated checks, and the public dashboard demonstrates match analytics, tactical previews, production-style empty states, Monte Carlo tournament probabilities, single-run tournament path simulation, Golden Boot and Tournament MVP modelling, and real/named demo player profiles.

This is a production-style graduate software engineering, backend engineering and data engineering portfolio project. It is intentionally not a gambling product: predictions are probabilistic football analytics, educational modelling and transparent simulation.

## Live Demo

Frontend: https://scouts-edge.vercel.app  
Tournament simulation: https://scouts-edge.vercel.app/tournament  
Backend API: https://scouts-edge.onrender.com  
API health: https://scouts-edge.onrender.com/health  
API docs: https://scouts-edge.onrender.com/docs  

Note: The backend/database are hosted on free-tier infrastructure, so the first request may take a few seconds to wake up.

## Screenshots

Screenshots:

- `docs/screenshots/dashboard.png`
- `docs/screenshots/match-completed.png`
- `docs/screenshots/match-scheduled.png`
- `docs/screenshots/tournament.png`
- `docs/screenshots/simulation-result.png`

## What It Solves

Football data is noisy and spread across providers. This project shows how to normalize match and event data, calculate tactical metrics, run transparent reference-model forecasts, simulate tournament paths, and expose the results through a clean full-stack product.

## Key Features

- FastAPI backend with domain-based route modules.
- PostgreSQL schema for teams, players, matches, events, predictions and reports.
- Offline demo mode with a 48-team World Cup-style demo dataset for engineering purposes.
- Curated real-player profile seed data for scorer candidates and team pages.
- Twelve groups of four teams and 72 generated group-stage fixtures.
- Provider interface for future StatsBomb Open Data and API-Football integrations.
- Deterministic analytics for shots, shot maps, possession chains, final-third entries, box entries, dangerous actions and set pieces.
- Transparent Poisson-style match prediction model.
- Full tournament Monte Carlo simulation from group stage to Round of 32, Round of 16, quarter-finals, semi-finals, final and winner.
- Scorer candidate, goal-type, Golden Boot and tournament MVP simulation modules.
- Rule-based match report generator that does not invent unavailable metrics.
- Scheduled-match empty states that show pre-match tactical previews when event data is not available.
- Next.js, TypeScript and Tailwind dashboard.
- Docker Compose setup and pytest coverage.

## Architecture

See [docs/architecture.md](docs/architecture.md).

Production:

```text
User Browser
  -> Vercel Next.js Frontend
  -> Render FastAPI Backend
  -> Neon PostgreSQL
```

Local development:

```text
User Browser
  -> Next.js dev server
  -> FastAPI dev server
  -> Docker PostgreSQL
```

## Tech Stack

- Backend: Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, Pandas/NumPy-ready services, pytest.
- Database: PostgreSQL.
- Frontend: Next.js, TypeScript, Tailwind CSS, Recharts, lucide-react.
- DevOps: Docker, Docker Compose for local development, Vercel-ready frontend, Docker-compatible backend, GitHub Actions.

## Local Setup

```bash
cd scouts-edge
cp .env.example .env
make docker-up
```

In another terminal:

```bash
make migrate
make seed-world-cup
```

The dashboard runs at `http://localhost:3000` and the API at `http://localhost:8000`.

Docker Compose is for local development only. It is not the production deployment architecture.

## Production Deployment

The live production split is:

- Frontend dashboard: Vercel hosts `frontend/`.
- Backend API: Render hosts the Docker-compatible FastAPI service from `backend/`.
- Database: Neon hosts PostgreSQL.

Render environment variables include `DATABASE_URL` and `CORS_ORIGINS`. Vercel environment variables include `NEXT_PUBLIC_API_BASE_URL`. Docker Compose is local-only and is not the production deployment setup.

See [docs/deployment.md](docs/deployment.md).

## CI/CD

- GitHub Actions runs backend tests, backend Ruff lint checks and the frontend production build.
- Vercel automatically deploys frontend changes from GitHub.
- Render deploys backend changes from GitHub.
- Deployment configuration uses environment variables instead of committed secrets.

## Security and Secrets

- No API keys or database URLs should be committed.
- `DATABASE_URL` lives only in Render environment variables.
- `NEXT_PUBLIC_API_BASE_URL` is safe to expose because it only points to the public API.
- CORS is restricted to local development origins and the Vercel production URL.
- The app is a public portfolio demo and does not store user accounts or sensitive user data.
- Future hardening could include rate limiting, auth for admin routes, stricter CORS per environment, and disabling public docs in production.

## Operational Notes

- Closing the browser or laptop does not stop the hosted deployment.
- Free-tier infrastructure may sleep and wake on the first request.
- New commits to `main` trigger redeploys depending on Vercel and Render project settings.
- The hosted database needs migrations and seed data when reset or recreated.

## API Overview

- `GET /health`
- `GET /teams`
- `GET /teams/{team_id}`
- `GET /teams/{team_id}/analytics`
- `GET /matches`
- `GET /matches/{match_id}`
- `GET /matches/{match_id}/events`
- `GET /matches/{match_id}/analytics`
- `GET /matches/{match_id}/shot-map`
- `GET /matches/{match_id}/possession-chains`
- `POST /predictions/match/{match_id}`
- `GET /predictions/match/{match_id}`
- `POST /predictions/tournament/simulate`
- `GET /predictions/tournament/latest`
- `GET /predictions/scorers/{match_id}`
- `GET /predictions/goal-types/{match_id}`
- `POST /reports/match/{match_id}`
- `GET /reports/{report_id}`

## Prediction Methodology

See [docs/prediction-model.md](docs/prediction-model.md). The model uses transparent team-strength ratings, expected goals, a Poisson-style scoreline grid and Monte Carlo simulation. It avoids betting odds, staking language and bookmaker integration.

## Tournament Simulation

The offline tournament mode uses a clearly labelled demo dataset, not official FIFA fixtures. It creates 12 groups of 4 teams, generates 6 demo fixtures per group, simulates the full group stage, advances the top 2 from each group plus the best 8 third-place teams, and then runs a deterministic Round of 32 bracket through the final. A separate single-run simulator produces one tournament path with group tables, knockout bracket, final score, top scorers, Golden Boot and tournament MVP.

See [docs/tournament-simulation.md](docs/tournament-simulation.md).

## Data Model

See [docs/data-model.md](docs/data-model.md).

## Player Profiles

Player profiles are curated demo seed data for engineering purposes. The data layer is designed so these profiles can be replaced by official FIFA squad lists or football API provider data.

The local importer checks for `data/raw/SquadLists-English.pdf` as a future official-source hook and falls back to `data/seed/player_profiles.csv` so the project remains demoable without the PDF.

## Tests

```bash
cd scouts-edge
make setup
make test
```

Tests cover analytics calculations, prediction probability shape, tournament simulation output, scorer predictions, goal-type predictions and the health endpoint.

## Recruiter Quick Start

- Live demo: https://scouts-edge.vercel.app
- API docs: https://scouts-edge.onrender.com/docs
- Local setup:

```bash
cp .env.example .env
make docker-up
```

- Tests:

```bash
cd backend
.venv/bin/python -m pytest
.venv/bin/ruff check app

cd ../frontend
npm run build
```

## Limitations

- The MVP uses a seeded 48-team demo tournament dataset, not official FIFA fixture data.
- Player profiles are curated demo seed data and are not guaranteed official final squads.
- The prediction engine is a transparent reference model, not a calibrated professional forecasting model.
- The API-Football provider is scaffolded but intentionally does not require credentials.
- PDF reporting and LLM narrative generation are future enhancements.

## Future Improvements

- Parse real StatsBomb Open Data JSON into the normalized event schema.
- Add backtesting and calibration reports.
- Persist API-generated predictions and reports in PostgreSQL.
- Add role-based auth for private dashboards.
- Generate PDF reports.
- Add self-hosted n8n workflows for scheduled ingestion and alerts.
- Add provider-specific deployment manifests for Render, Railway, Fly.io, or a VPS.

## GitHub Readiness Checklist

- Backend tests passing.
- Backend Ruff lint passing.
- Frontend build passing.
- Screenshots added to `docs/screenshots`.
- No API keys committed.
- `.env.example` present.
- README explains limitations.
- Demo data labelled honestly.
- Player profiles no longer use placeholder names.
- Simulation button works.
- Full tournament simulation working.
- Seed data loads 48 demo teams.
- Dashboard shows group tables.
- Dashboard shows full tournament stage probabilities.
- Match detail pages have scheduled-match empty states.
- Shot map explains missing event data.

## Portfolio Value / Engineering Highlights

- Full-stack monorepo with clear backend/frontend boundaries.
- Typed frontend built with Next.js, TypeScript and reusable dashboard components.
- REST API design using FastAPI route modules and Pydantic schemas.
- Relational data modelling for teams, players, matches, events, predictions and reports.
- Deterministic analytics for shot maps, possession chains, set pieces and tactical summaries.
- Monte Carlo simulation for 48-team tournament stage probabilities.
- Single-run tournament simulation for one complete bracket path and final score.
- Player-level awards modelling for scorer candidates, Golden Boot and Tournament MVP.
- CORS/debugging fix separating browser-safe API URLs from Docker/server-only URLs.
- Deployment across Vercel, Render and Neon.
- GitHub Actions CI checks for backend tests/lint and frontend build.
- Docker Compose local setup for repeatable development.

## What I Learned

- Designing a normalized football analytics data model.
- Building transparent prediction services that are easy to explain.
- Structuring a full-stack monorepo with Docker and CI.
- Turning raw event-style data into dashboard-ready metrics.

## CV Bullets

- Built a full-stack football analytics platform using FastAPI, PostgreSQL, Next.js, Docker, and TypeScript.
- Implemented a 48-team tournament simulation engine covering group-stage qualification, best third-place ranking, knockout progression, and Monte Carlo forecasting.
- Designed player-level simulation logic for likely scorers, Golden Boot, and tournament MVP using transparent weighted features.
- Added production-style empty states, API validation, tests, CI, and deployment documentation for a Vercel + hosted FastAPI architecture.
