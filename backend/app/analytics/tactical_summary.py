from __future__ import annotations

from typing import Any


def completed_match_summary(
    match: dict[str, Any],
    analytics: dict[str, Any],
    chains: list[dict[str, Any]],
    involvement: list[dict[str, Any]],
) -> dict[str, Any]:
    home = match["home_team"]
    away = match["away_team"]
    home_metrics = analytics["teams"].get(match["home_team_id"], {})
    away_metrics = analytics["teams"].get(match["away_team_id"], {})
    top_involvement = involvement[:3]
    return {
        "mode": "completed_match",
        "headline": f"{home['name']} vs {away['name']} event-data tactical summary",
        "summary": (
            f"{home['name']} produced {home_metrics.get('total_shots', 0)} shots and "
            f"{home_metrics.get('xg', 0)} xG, while {away['name']} produced "
            f"{away_metrics.get('total_shots', 0)} shots and {away_metrics.get('xg', 0)} xG. "
            f"The event feed contains {len(chains)} possession chains and supports shot-map, set-piece, "
            "dangerous-action and player-involvement analysis."
        ),
        "bullets": [
            f"{home['name']} set-piece threat score: {home_metrics.get('set_piece_threat_score', 0)}.",
            f"{away['name']} set-piece threat score: {away_metrics.get('set_piece_threat_score', 0)}.",
            f"Final-third entries: {home['name']} {home_metrics.get('final_third_entries', 0)}, {away['name']} {away_metrics.get('final_third_entries', 0)}.",
            f"Top involvement player ids: {', '.join(str(item['player_id']) for item in top_involvement) if top_involvement else 'not available'}.",
        ],
    }


def pre_match_preview(
    match: dict[str, Any],
    prediction: dict[str, Any],
    scorers: dict[str, Any],
    goal_types: dict[str, Any],
) -> dict[str, Any]:
    home = match["home_team"]
    away = match["away_team"]
    home_rating = home["rating"]
    away_rating = away["rating"]
    top_scorers = scorers["candidates"][:3]

    if home_rating["open_play_threat"] > away_rating["open_play_threat"]:
        open_play_note = f"{home['name']} profile as the stronger open-play side."
    elif away_rating["open_play_threat"] > home_rating["open_play_threat"]:
        open_play_note = f"{away['name']} profile as the stronger open-play side."
    else:
        open_play_note = "Both teams have similar open-play threat ratings."

    set_piece_edge = home if home_rating["set_piece_threat"] >= away_rating["set_piece_threat"] else away
    confidence = prediction["confidence"]
    return {
        "mode": "pre_match",
        "headline": "Pre-match tactical preview",
        "summary": (
            f"No event data is available yet for this {match['status']} fixture. "
            f"{open_play_note} {set_piece_edge['name']} carry the stronger seeded set-piece threat. "
            f"The model projects expected goals of {prediction['team_a_expected_goals']} for {home['name']} "
            f"and {prediction['team_b_expected_goals']} for {away['name']}, with {confidence.lower()} confidence."
        ),
        "bullets": [
            f"{home['name']} attack/defence/form: {home_rating['attack_strength']:.2f} / {home_rating['defence_strength']:.2f} / {home_rating['recent_form']:.2f}.",
            f"{away['name']} attack/defence/form: {away_rating['attack_strength']:.2f} / {away_rating['defence_strength']:.2f} / {away_rating['recent_form']:.2f}.",
            f"Likely scorer candidates: {', '.join(candidate['player'] for candidate in top_scorers)}.",
            "Shot maps and possession-chain analysis require ingested event data.",
        ],
        "goal_type_probabilities": goal_types["teams"],
        "confidence": confidence,
    }
