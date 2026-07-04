# The Scout's Edge

The Scout's Edge is a full-stack football analytics and tournament simulation platform built with FastAPI, PostgreSQL, Next.js, TypeScript and Docker. It combines match analytics, transparent forecasting, 48-team tournament simulation, named player profiles and player-level awards simulation in a production-style graduate software/data engineering portfolio project.

This is a production-style MVP for a graduate software engineering, backend engineering and data engineering portfolio. It is intentionally not a gambling product: predictions are probabilistic football analytics, educational modelling and transparent simulation.

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

## Deployment

The intended production split is:

- Frontend dashboard: deploy `frontend/` to Vercel.
- PostgreSQL database: use Neon Postgres or Supabase Postgres.
- FastAPI backend: keep `backend/` Docker-compatible and deploy it to Render, Railway, Fly.io, or a VPS.

Set `NEXT_PUBLIC_API_BASE_URL` in Vercel to the public FastAPI backend URL. Set `DATABASE_URL` on the backend host to the hosted Postgres connection string. Set `CORS_ORIGINS` on the backend host to include the Vercel dashboard domain.

See [docs/deployment.md](docs/deployment.md).

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
