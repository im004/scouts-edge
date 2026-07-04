from __future__ import annotations

from typing import Any


def predict_goal_types(team: dict[str, Any], opponent: dict[str, Any], rating: dict[str, float], opponent_rating: dict[str, float], match_id: int) -> dict[str, Any]:
    open_play = min(0.78, 0.22 + rating["open_play_threat"] * 0.42 + rating["attack_strength"] * 0.16)
    set_piece = min(0.50, 0.06 + rating["set_piece_threat"] * 0.28 + opponent_rating["set_piece_weakness"] * 0.14)
    penalty = min(0.20, 0.05 + rating["attack_strength"] * 0.05)
    counter = min(0.40, 0.06 + max(0.0, opponent_rating["attack_strength"] - rating["defence_strength"]) * 0.18 + rating["recent_form"] * 0.08)
    confidence = "Medium" if rating["set_piece_threat"] > 0.68 or rating["open_play_threat"] > 0.80 else "Low"
    return {
        "match_id": match_id,
        "team": team["name"],
        "open_play_goal_probability": round(open_play, 3),
        "set_piece_goal_probability": round(set_piece, 3),
        "penalty_goal_probability": round(penalty, 3),
        "counterattack_goal_probability": round(counter, 3),
        "confidence": confidence,
        "explanation": [
            f"{team['name']} open-play threat and attack strength drive the open-play estimate.",
            f"{opponent['name']} set-piece weakness is included for dead-ball scenarios.",
            "Penalty and counterattack estimates use conservative reference weights until richer event data is connected.",
        ],
    }
