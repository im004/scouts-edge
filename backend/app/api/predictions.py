from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.predictions.goal_types import predict_goal_types
from app.predictions.match import predict_match
from app.predictions.scorers import predict_scorers
from app.predictions.tournament import simulate_tournament
from app.schemas.common import SimulationRequest
from app.services import demo_data

router = APIRouter(prefix="/predictions", tags=["predictions"])

_LATEST_SIMULATION: dict | None = None
_MATCH_PREDICTIONS: dict[int, dict] = {}


def _match_context(match_id: int) -> tuple[dict, dict, dict, dict, dict]:
    try:
        match = demo_data.match_by_id(match_id)
        team_a = demo_data.team_by_id(match["home_team_id"])
        team_b = demo_data.team_by_id(match["away_team_id"])
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Match not found") from exc
    return match, team_a, team_b, demo_data.TEAM_RATINGS[team_a["id"]], demo_data.TEAM_RATINGS[team_b["id"]]


@router.post("/match/{match_id}")
def create_match_prediction(match_id: int) -> dict:
    match, team_a, team_b, rating_a, rating_b = _match_context(match_id)
    prediction = predict_match(match["id"], team_a, team_b, rating_a, rating_b)
    _MATCH_PREDICTIONS[match_id] = prediction
    return prediction


@router.get("/match/{match_id}")
def get_match_prediction(match_id: int) -> dict:
    if match_id not in _MATCH_PREDICTIONS:
        return create_match_prediction(match_id)
    return _MATCH_PREDICTIONS[match_id]


@router.post("/tournament/simulate")
def run_tournament_simulation(request: SimulationRequest) -> dict:
    global _LATEST_SIMULATION
    runs = min(max(request.runs, 100), 10000)
    _LATEST_SIMULATION = simulate_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, runs=runs, seed=request.seed)
    return _LATEST_SIMULATION


@router.get("/tournament/latest")
def get_latest_tournament_simulation() -> dict:
    global _LATEST_SIMULATION
    if _LATEST_SIMULATION is None:
        _LATEST_SIMULATION = simulate_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, runs=1000)
    return _LATEST_SIMULATION


@router.get("/scorers/{match_id}")
def get_scorer_predictions(match_id: int) -> dict:
    _, team_a, team_b, rating_a, rating_b = _match_context(match_id)
    match_prediction = get_match_prediction(match_id)
    candidates = predict_scorers(team_a, demo_data.players_for_team(team_a["id"]), match_prediction["team_a_expected_goals"])
    candidates.extend(predict_scorers(team_b, demo_data.players_for_team(team_b["id"]), match_prediction["team_b_expected_goals"]))
    return {"match_id": match_id, "candidates": sorted(candidates, key=lambda item: item["anytime_scorer_probability"], reverse=True)}


@router.get("/goal-types/{match_id}")
def get_goal_type_predictions(match_id: int) -> dict:
    _, team_a, team_b, rating_a, rating_b = _match_context(match_id)
    return {
        "match_id": match_id,
        "teams": [
            predict_goal_types(team_a, team_b, rating_a, rating_b, match_id),
            predict_goal_types(team_b, team_a, rating_b, rating_a, match_id),
        ],
    }
