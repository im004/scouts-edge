from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, matches, predictions, reports, teams, tournament
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Automated football analytics and World Cup prediction dashboard API.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(teams.router)
    app.include_router(matches.router)
    app.include_router(predictions.router)
    app.include_router(tournament.router)
    app.include_router(reports.router)
    return app


app = create_app()
