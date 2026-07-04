from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.analytics.match import calculate_match_analytics
from app.api.predictions import get_goal_type_predictions, get_match_prediction, get_scorer_predictions
from app.reports.narrative import ReportNarrativeService
from app.services import demo_data

router = APIRouter(prefix="/reports", tags=["reports"])
_REPORTS: dict[int, dict] = {}


@router.post("/match/{match_id}")
def create_report(match_id: int) -> dict:
    try:
        match = demo_data.enriched_match(demo_data.match_by_id(match_id))
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="Match not found") from exc
    events = demo_data.events_for_match(match_id)
    analytics = calculate_match_analytics(events, [match["home_team_id"], match["away_team_id"]])
    prediction = get_match_prediction(match_id)
    scorers = get_scorer_predictions(match_id)
    goal_types = get_goal_type_predictions(match_id)
    content = ReportNarrativeService().generate(match, analytics, prediction, scorers, goal_types)
    report_id = len(_REPORTS) + 1
    report = {
        "id": report_id,
        "match_id": match_id,
        "title": f"{match['home_team']['name']} vs {match['away_team']['name']} scouting report",
        "format": "markdown",
        "content": content,
    }
    _REPORTS[report_id] = report
    return report


@router.get("/{report_id}")
def get_report(report_id: int) -> dict:
    if report_id not in _REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    return _REPORTS[report_id]
