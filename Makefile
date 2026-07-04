.PHONY: setup dev test lint migrate seed seed-world-cup simulate docker-up docker-down

setup:
	cd backend && python -m pip install -e ".[dev]"
	cd frontend && npm install

dev:
	$(MAKE) -j2 backend-dev frontend-dev

backend-dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd frontend && npm run dev

test:
	cd backend && pytest

lint:
	cd backend && ruff check app
	cd frontend && npm run lint

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.ingestion.seed_world_cup

seed-world-cup:
	cd backend && python -m app.ingestion.seed_world_cup

simulate:
	curl -X POST http://localhost:8000/predictions/tournament/simulate \
		-H "Content-Type: application/json" \
		-d '{"runs":1000,"seed":7}'

docker-up:
	docker compose up --build

docker-down:
	docker compose down
