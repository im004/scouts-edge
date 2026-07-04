from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.predictions.single_tournament import run_single_tournament
from app.predictions.tournament import generate_group_fixtures, groups_from_teams, simulate_single_tournament, simulate_tournament
from app.schemas.common import SimulationRequest, SingleSimulationRunRequest
from app.services import demo_data

router = APIRouter(prefix="/tournament", tags=["tournament"])

_LATEST_SIMULATION: dict | None = None
_LATEST_SINGLE_RUN: dict | None = None


@router.get("/groups")
def get_groups() -> dict:
    return {
        "dataset_label": demo_data.DATASET_LABEL,
        "groups": {
            group: [{**team, "rating": demo_data.TEAM_RATINGS[team["id"]]} for team in teams]
            for group, teams in groups_from_teams(demo_data.TEAMS).items()
        },
    }


@router.get("/groups/{group_name}")
def get_group(group_name: str) -> dict:
    normalized = group_name.replace("-", " ").title()
    if not normalized.startswith("Group "):
        normalized = f"Group {normalized[-1].upper()}"
    groups = groups_from_teams(demo_data.TEAMS)
    if normalized not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"group": normalized, "teams": groups[normalized]}


@router.get("/fixtures")
def get_fixtures() -> dict:
    return {"fixtures": generate_group_fixtures(demo_data.TEAMS), "fixture_count": 72}


@router.post("/simulate")
def run_simulation(request: SimulationRequest) -> dict:
    global _LATEST_SIMULATION
    _LATEST_SIMULATION = simulate_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, runs=request.runs, seed=request.seed)
    return _LATEST_SIMULATION


@router.get("/simulate/latest")
def get_latest_simulation() -> dict:
    global _LATEST_SIMULATION
    if _LATEST_SIMULATION is None:
        _LATEST_SIMULATION = simulate_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, runs=1000, seed=7)
    return _LATEST_SIMULATION


@router.get("/bracket/latest")
def get_latest_bracket() -> dict:
    latest = get_latest_simulation()
    return {"mode": latest["mode"], "bracket": latest["bracket"], "winner": latest["winner"]}


@router.get("/third-place-table/latest")
def get_latest_third_place_table() -> dict:
    latest = get_latest_simulation()
    return {
        "third_place_ranking": latest["third_place_ranking"],
        "selected_third_place_qualifiers": latest["selected_third_place_qualifiers"],
    }


@router.get("/single-run")
def get_single_run(seed: int = 7) -> dict:
    return simulate_single_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, seed=seed)


@router.post("/simulate/run")
def run_single_simulation(request: SingleSimulationRunRequest) -> dict:
    global _LATEST_SINGLE_RUN
    _LATEST_SINGLE_RUN = run_single_tournament(seed=request.seed, include_awards=request.include_awards)
    return _LATEST_SINGLE_RUN
