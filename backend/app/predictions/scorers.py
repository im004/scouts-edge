from __future__ import annotations

from typing import Any


def predict_scorers(team: dict[str, Any], players: list[dict[str, Any]], team_expected_goals: float) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for player in players:
        if player.get("position") == "GK":
            continue
        features = player["features"]
        minutes_factor = features["expected_minutes"] / 90
        baseline = (
            features["xg_per_90"] * 0.45
            + features["goals_per_90"] * 0.25
            + features["shots_per_90"] * 0.035
            + team_expected_goals * 0.08
            + features["recent_form"] * 0.05
        )
        role_bonus = (
            (0.045 if features["penalty_taker"] else 0.0)
            + (0.025 if features.get("set_piece_target") else 0.0)
            + (0.02 if features.get("set_piece_taker") else 0.0)
            + (0.02 if features.get("creative_threat") else 0.0)
        )
        anytime = min(0.72, max(0.03, (baseline + role_bonus) * minutes_factor * features["starting_probability"]))
        first = anytime * 0.28
        confidence = "Medium" if features["starting_probability"] > 0.75 and features["expected_minutes"] > 70 else "Low"
        if features["xg_per_90"] >= 0.45 and features["expected_minutes"] >= 75:
            top_factor = "High xG per 90 and expected minutes"
        elif features.get("penalty_taker"):
            top_factor = "Penalty role boosts scoring probability"
        elif features.get("creative_threat"):
            top_factor = "Creative role and shot volume support chance involvement"
        else:
            top_factor = "Expected minutes and team expected goals drive the estimate"
        explanation = [
            f"Uses xG/90, shots/90, expected minutes and {team['name']} expected goals.",
            "Penalty, set-piece, aerial and creative roles are included as transparent role adjustments.",
        ]
        probability = round(anytime, 3)
        feature_payload = {
            "expected_minutes": features["expected_minutes"],
            "goals_per_90": features["goals_per_90"],
            "shots_per_90": features["shots_per_90"],
            "xg_per_90": features["xg_per_90"],
            "penalty_taker": features["penalty_taker"],
            "set_piece_taker": features.get("set_piece_taker", False),
            "aerial_threat": features.get("aerial_threat", False),
            "creative_threat": features.get("creative_threat", False),
        }
        candidates.append(
            {
                "player_name": player["name"],
                "team_name": team["name"],
                "team_code": player.get("team_code", team.get("short_name")),
                "position": player.get("position"),
                "role": player.get("role"),
                "probability": probability,
                "top_factor": top_factor,
                "features": feature_payload,
                "player": player["name"],
                "team": team["name"],
                "anytime_scorer_probability": probability,
                "first_scorer_probability": round(first, 3),
                "confidence": confidence,
                "explanation": explanation,
            }
        )
    return sorted(candidates, key=lambda item: item["probability"], reverse=True)
