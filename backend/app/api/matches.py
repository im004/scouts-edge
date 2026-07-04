from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.analytics.match import calculate_match_analytics, player_involvement, possession_chains, shot_map
from app.analytics.tactical_summary import completed_match_summary, pre_match_preview
from app.predictions.goal_types import predict_goal_types
from app.predictions.match import predict_match
from app.predictions.scorers import predict_scorers
from app.services import demo_data

router = APIRouter(prefix="/matches", tags=["matches"])


def _match_or_404(match_id: int) -> dict:
    try:
        return demo_data.match_by_id(match_id)
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Match not found") from exc


@router.get("")
def list_matches(
    team: str | None = None,
    status: str | None = None,
    stage: str | None = None,
    group: str | None = None,
) -> list[dict]:
    matches = [demo_data.enriched_match(match) for match in demo_data.MATCHES]
    if team:
        team_lower = team.lower()
        matches = [
            match
            for match in matches
            if team_lower in match["home_team"]["name"].lower() or team_lower in match["away_team"]["name"].lower()
        ]
    if status:
        matches = [match for match in matches if match["status"] == status]
    if stage:
        matches = [match for match in matches if match["stage"] == stage]
    if group:
        matches = [match for match in matches if match.get("group", "").lower() == group.lower()]
    return matches


@router.get("/{match_id}")
def get_match(match_id: int) -> dict:
    return demo_data.enriched_match(_match_or_404(match_id))


@router.get("/{match_id}/events")
def get_events(match_id: int) -> list[dict]:
    _match_or_404(match_id)
    return demo_data.events_for_match(match_id)


@router.get("/{match_id}/analytics")
def get_match_analytics(match_id: int) -> dict:
    match = demo_data.enriched_match(_match_or_404(match_id))
    events = demo_data.events_for_match(match_id)
    if not events:
        team_a = match["home_team"]
        team_b = match["away_team"]
        rating_a = demo_data.TEAM_RATINGS[team_a["id"]]
        rating_b = demo_data.TEAM_RATINGS[team_b["id"]]
        prediction = predict_match(match_id, team_a, team_b, rating_a, rating_b)
        scorers = {
            "candidates": sorted(
                predict_scorers(team_a, demo_data.players_for_team(team_a["id"]), prediction["team_a_expected_goals"])
                + predict_scorers(team_b, demo_data.players_for_team(team_b["id"]), prediction["team_b_expected_goals"]),
                key=lambda item: item["anytime_scorer_probability"],
                reverse=True,
            )
        }
        goal_types = {
            "teams": [
                predict_goal_types(team_a, team_b, rating_a, rating_b, match_id),
                predict_goal_types(team_b, team_a, rating_b, rating_a, match_id),
            ]
        }
        return {
            "mode": "pre_match",
            "has_event_data": False,
            "message": "No event data available yet. Showing pre-match tactical preview based on team ratings, player profiles, and seeded tendencies.",
            "pre_match_preview": pre_match_preview(match, prediction, scorers, goal_types),
            "teams": {},
            "player_involvement": [],
        }
    analytics = calculate_match_analytics(events, [match["home_team_id"], match["away_team_id"]])
    involvement = player_involvement(events)
    chains = possession_chains(events)
    analytics["mode"] = "completed_match" if match["status"] == "completed" else match["status"]
    analytics["has_event_data"] = True
    analytics["player_involvement"] = involvement
    analytics["tactical_summary"] = completed_match_summary(match, analytics, chains, involvement)
    return analytics


@router.get("/{match_id}/shot-map")
def get_shot_map(match_id: int) -> dict:
    match = _match_or_404(match_id)
    teams = {team["id"]: team["name"] for team in demo_data.TEAMS}
    players = {player["id"]: player["name"] for player in demo_data.PLAYERS}
    shots = shot_map(demo_data.events_for_match(match_id), teams, players)
    if not shots:
        return {
            "has_shots": False,
            "shots": [],
            "empty_state": {
                "title": "No shot map available yet",
                "match_status": match["status"],
                "has_event_data": False,
                "explanation": "No shot map available yet because this match has no event data. Shot maps are generated after event data is ingested.",
                "required_data": "Shot events with x/y coordinates, player, team, minute, outcome and xG fields.",
                "next_action": "Ingest event data or view the pre-match tactical preview.",
            },
        }
    return {"has_shots": True, "shots": shots, "empty_state": None}


@router.get("/{match_id}/possession-chains")
def get_possessions(match_id: int) -> list[dict]:
    _match_or_404(match_id)
    return possession_chains(demo_data.events_for_match(match_id))
