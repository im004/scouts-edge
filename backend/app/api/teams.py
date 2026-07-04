from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services import demo_data

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("")
def list_teams() -> list[dict]:
    return [{**team, "rating": demo_data.TEAM_RATINGS[team["id"]]} for team in demo_data.TEAMS]


@router.get("/{team_id}")
def get_team(team_id: int) -> dict:
    try:
        team = demo_data.team_by_id(team_id)
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc
    return {
        **team,
        "rating": demo_data.TEAM_RATINGS[team_id],
        "players": demo_data.players_for_team(team_id),
    }


@router.get("/{team_id}/analytics")
def get_team_analytics(team_id: int) -> dict:
    try:
        team = demo_data.team_by_id(team_id)
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc
    events = [event for match in demo_data.MATCHES for event in demo_data.events_for_match(match["id"]) if event["team_id"] == team_id]
    shots = [event for event in events if event["event_type"] == "Shot"]
    return {
        "team": team,
        "rating": demo_data.TEAM_RATINGS[team_id],
        "recent_match_metrics": {
            "events": len(events),
            "shots": len(shots),
            "xg": round(sum(float(shot.get("xg") or 0) for shot in shots), 2),
            "set_piece_shots": len([shot for shot in shots if shot.get("play_pattern") in {"From Corner", "From Free Kick"}]),
        },
    }
