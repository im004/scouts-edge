from __future__ import annotations

import math
from typing import Any


def _poisson(k: int, lam: float) -> float:
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def expected_goals(team_rating: dict[str, float], opponent_rating: dict[str, float], neutral_venue: bool = True) -> float:
    attack = team_rating["attack_strength"]
    opponent_defence = opponent_rating["defence_strength"]
    form = team_rating["recent_form"]
    base = 1.15 + (attack - 0.70) * 1.8 - (opponent_defence - 0.70) * 1.25 + (form - 0.50) * 0.55
    venue_adjustment = 0.0 if neutral_venue else 0.12
    return round(max(0.25, min(3.2, base + venue_adjustment)), 2)


def predict_match(
    match_id: int,
    team_a: dict[str, Any],
    team_b: dict[str, Any],
    rating_a: dict[str, float],
    rating_b: dict[str, float],
    neutral_venue: bool = True,
) -> dict[str, Any]:
    xg_a = expected_goals(rating_a, rating_b, neutral_venue)
    xg_b = expected_goals(rating_b, rating_a, True)
    score_probs: list[dict[str, Any]] = []
    a_win = draw = b_win = 0.0

    for goals_a in range(0, 6):
        for goals_b in range(0, 6):
            probability = _poisson(goals_a, xg_a) * _poisson(goals_b, xg_b)
            score_probs.append({"score": f"{goals_a}-{goals_b}", "probability": probability})
            if goals_a > goals_b:
                a_win += probability
            elif goals_a == goals_b:
                draw += probability
            else:
                b_win += probability

    total = a_win + draw + b_win
    a_win, draw, b_win = a_win / total, draw / total, b_win / total
    confidence = "High" if abs(a_win - b_win) > 0.22 else "Medium" if abs(a_win - b_win) > 0.08 else "Low"
    most_likely = sorted(score_probs, key=lambda item: item["probability"], reverse=True)[:5]

    explanation = [
        f"{team_a['name']} attack rating is {rating_a['attack_strength']:.2f} against {team_b['name']} defence {rating_b['defence_strength']:.2f}.",
        f"{team_b['name']} attack rating is {rating_b['attack_strength']:.2f} against {team_a['name']} defence {rating_a['defence_strength']:.2f}.",
    ]
    if rating_a["recent_form"] > rating_b["recent_form"]:
        explanation.append(f"{team_a['name']} have the stronger recent-form input in the current model.")
    elif rating_b["recent_form"] > rating_a["recent_form"]:
        explanation.append(f"{team_b['name']} have the stronger recent-form input in the current model.")
    else:
        explanation.append("Both teams have similar recent-form inputs.")

    return {
        "match_id": match_id,
        "team_a": team_a["name"],
        "team_b": team_b["name"],
        "team_a_win_probability": round(a_win, 3),
        "draw_probability": round(draw, 3),
        "team_b_win_probability": round(b_win, 3),
        "team_a_expected_goals": xg_a,
        "team_b_expected_goals": xg_b,
        "most_likely_scorelines": [
            {"score": item["score"], "probability": round(item["probability"], 3)} for item in most_likely
        ],
        "confidence": confidence,
        "explanation": explanation,
    }
