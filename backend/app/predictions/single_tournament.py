from __future__ import annotations

import random
import uuid
from typing import Any

from app.predictions.tournament import simulate_single_tournament
from app.services import demo_data

STAGE_BONUS = {
    "Group Stage": 0.0,
    "Round of 32": 0.4,
    "Round of 16": 0.8,
    "Quarter-final": 1.3,
    "Semi-final": 2.0,
    "Final": 3.0,
    "Winner": 4.0,
}
STAGE_RANK = {
    "Group stage": 0,
    "Round of 32": 1,
    "Round of 16": 2,
    "Quarter-final": 3,
    "Semi-finalist": 4,
    "Runner-up": 5,
    "Winner": 6,
}


def _team_by_name() -> dict[str, dict[str, Any]]:
    return {team["name"]: team for team in demo_data.TEAMS}


def _players_for_team_name(team_name: str) -> list[dict[str, Any]]:
    team = _team_by_name()[team_name]
    return demo_data.players_for_team(team["id"])


def _weighted_choice(items: list[dict[str, Any]], weights: list[float], rng: random.Random) -> dict[str, Any]:
    total = sum(weights)
    if total <= 0:
        return items[0]
    draw = rng.random() * total
    cumulative = 0.0
    for item, weight in zip(items, weights, strict=True):
        cumulative += weight
        if draw <= cumulative:
            return item
    return items[-1]


def _scorer_weight(player: dict[str, Any], goal_context: str) -> float:
    features = player["features"]
    position = player["position"]
    position_bonus = 1.8 if position == "FW" else 1.15 if position == "MF" else 0.42
    weight = (
        features["xg_per_90"] * 4.0
        + features["goals_per_90"] * 3.0
        + features["shots_per_90"] * 0.35
        + features["starting_probability"]
        + position_bonus
    )
    if goal_context == "penalty" and features.get("penalty_taker"):
        weight += 2.4
    if goal_context == "set_piece" and features.get("aerial_threat"):
        weight += 1.5
    if features.get("set_piece_taker"):
        weight += 0.2
    return max(0.05, weight)


def _assist_weight(player: dict[str, Any], goal_context: str) -> float:
    features = player["features"]
    weight = features["creative_threat"] * 2.2 + features.get("set_piece_taker", False) * 1.5 + features["shots_per_90"] * 0.15
    if goal_context == "set_piece" and features.get("set_piece_taker"):
        weight += 1.6
    if player["position"] in {"MF", "FW"}:
        weight += 0.8
    return max(0.05, weight)


def _blank_player_stat(player: dict[str, Any]) -> dict[str, Any]:
    return {
        "player_name": player["player_name"],
        "team": player["team_name"],
        "team_code": player["team_code"],
        "position": player["position"],
        "role": player["role"],
        "goals": 0,
        "assists": 0,
        "minutes": 0.0,
        "knockout_goals": 0,
        "semi_final_goal_involvements": 0,
        "final_goal_involvements": 0,
        "team_stage_reached": "Group stage",
        "rating": 6.0,
    }


def _ensure_player(stats: dict[str, dict[str, Any]], player: dict[str, Any]) -> dict[str, Any]:
    key = f"{player['team_code']}::{player['player_name']}"
    if key not in stats:
        stats[key] = _blank_player_stat(player)
    return stats[key]


def _record_team_minutes(stats: dict[str, dict[str, Any]], team_name: str) -> None:
    for player in _players_for_team_name(team_name):
        stat = _ensure_player(stats, player)
        stat["minutes"] += float(player["features"]["expected_minutes"])


def _assign_goals_for_team(
    stats: dict[str, dict[str, Any]],
    team_name: str,
    goals: int,
    stage: str,
    rng: random.Random,
) -> None:
    players = [player for player in _players_for_team_name(team_name) if player["position"] != "GK"]
    for _ in range(goals):
        context_draw = rng.random()
        goal_context = "penalty" if context_draw < 0.08 else "set_piece" if context_draw < 0.30 else "open_play"
        scorer = _weighted_choice(players, [_scorer_weight(player, goal_context) for player in players], rng)
        scorer_stat = _ensure_player(stats, scorer)
        scorer_stat["goals"] += 1
        if stage != "Group Stage":
            scorer_stat["knockout_goals"] += 1
        if stage == "Semi-final":
            scorer_stat["semi_final_goal_involvements"] += 1
        if stage == "Final":
            scorer_stat["final_goal_involvements"] += 1

        if goal_context != "penalty" and rng.random() < 0.74:
            assist_pool = [player for player in players if player["id"] != scorer["id"]]
            assister = _weighted_choice(assist_pool, [_assist_weight(player, goal_context) for player in assist_pool], rng)
            assist_stat = _ensure_player(stats, assister)
            assist_stat["assists"] += 1
            if stage == "Semi-final":
                assist_stat["semi_final_goal_involvements"] += 1
            if stage == "Final":
                assist_stat["final_goal_involvements"] += 1


def _record_match_player_events(stats: dict[str, dict[str, Any]], match: dict[str, Any], rng: random.Random) -> None:
    _record_team_minutes(stats, match["team_a"])
    _record_team_minutes(stats, match["team_b"])
    _assign_goals_for_team(stats, match["team_a"], match["team_a_goals"], match["stage"], rng)
    _assign_goals_for_team(stats, match["team_b"], match["team_b_goals"], match["stage"], rng)


def _stage_reached_by_team(single: dict[str, Any], runner_up: str) -> dict[str, str]:
    names = {team["id"]: team["name"] for team in demo_data.TEAMS}
    reached: dict[str, str] = {team["name"]: "Group stage" for team in demo_data.TEAMS}
    for team_id in single["reached"]["round_of_32"]:
        reached[names[team_id]] = "Round of 32"
    for team_id in single["reached"]["round_of_16"]:
        reached[names[team_id]] = "Round of 16"
    for team_id in single["reached"]["quarter_final"]:
        reached[names[team_id]] = "Quarter-final"
    for team_id in single["reached"]["semi_final"]:
        reached[names[team_id]] = "Semi-finalist"
    for team_id in single["reached"]["final"]:
        reached[names[team_id]] = "Runner-up"
    reached[runner_up] = "Runner-up"
    reached[single["winner"]] = "Winner"
    return reached


def _score_awards(stats: dict[str, dict[str, Any]], stage_by_team: dict[str, str]) -> list[dict[str, Any]]:
    for stat in stats.values():
        stage = stage_by_team.get(stat["team"], "Group stage")
        stat["team_stage_reached"] = stage
        defensive_bonus = 0.8 if stat["position"] in {"DF", "GK"} and STAGE_RANK[stage] >= 4 else 0.0
        score = (
            stat["goals"] * 1.6
            + stat["assists"] * 1.0
            + stat["knockout_goals"] * 1.2
            + STAGE_RANK[stage] * 0.75
            + stat["semi_final_goal_involvements"] * 0.6
            + stat["final_goal_involvements"] * 1.0
            + defensive_bonus
        )
        stat["rating"] = round(min(10.0, 6.0 + score / 3.5), 2)
    return list(stats.values())


def _format_match(match: dict[str, Any]) -> dict[str, Any]:
    return {
        "team_a": match["team_a"],
        "team_b": match["team_b"],
        "score": f"{match['team_a_goals']}-{match['team_b_goals']}",
        "winner": match["winner"],
        "loser": match["loser"],
        "decided_by": match["decided_by"],
    }


def run_single_tournament(seed: int | None = None, include_awards: bool = True) -> dict[str, Any]:
    resolved_seed = seed if seed is not None else random.SystemRandom().randint(1, 999_999_999)
    rng = random.Random(resolved_seed)
    single = simulate_single_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, seed=resolved_seed)
    stats: dict[str, dict[str, Any]] = {}

    for match in single["group_stage"]["group_match_results"]:
        normalized = {
            "stage": "Group Stage",
            "team_a": match["home_team"],
            "team_b": match["away_team"],
            "team_a_goals": match["home_goals"],
            "team_b_goals": match["away_goals"],
        }
        _record_match_player_events(stats, normalized, rng)

    knockout_rounds = []
    for round_name in ["Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final"]:
        matches = single["bracket"][round_name]
        for match in matches:
            _record_match_player_events(stats, match, rng)
        knockout_rounds.append({"round": round_name, "matches": [_format_match(match) for match in matches]})

    final_match = single["bracket"]["Final"][0]
    runner_up_name = final_match["loser"]
    stage_by_team = _stage_reached_by_team(single, runner_up_name)
    leaderboard = _score_awards(stats, stage_by_team) if include_awards else []
    top_scorers = sorted(
        leaderboard,
        key=lambda stat: (-stat["goals"], -stat["assists"], stat["minutes"], -STAGE_RANK[stat["team_stage_reached"]], stat["player_name"]),
    )
    mvp_leaderboard = sorted(leaderboard, key=lambda stat: (-stat["rating"], -stat["goals"], -stat["assists"], stat["player_name"]))

    golden_boot = top_scorers[0] if top_scorers else None
    tournament_mvp = mvp_leaderboard[0] if mvp_leaderboard else None
    team_lookup = _team_by_name()
    semi_finalists = sorted({match["team_a"] for match in single["bracket"]["Semi-final"]} | {match["team_b"] for match in single["bracket"]["Semi-final"]})

    return {
        "simulation_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"scouts-edge-single-run-{resolved_seed}")),
        "seed": resolved_seed,
        "winner": team_lookup[single["winner"]],
        "runner_up": team_lookup[runner_up_name],
        "final": {
            "team_a": final_match["team_a"],
            "team_b": final_match["team_b"],
            "score": f"{final_match['team_a_goals']}-{final_match['team_b_goals']}",
            "decided_by": final_match["decided_by"],
        },
        "semi_finalists": [team_lookup[name] for name in semi_finalists],
        "group_tables": [
            {"group": group, "table": rows}
            for group, rows in single["group_stage"]["group_tables"].items()
        ],
        "third_place_table": single["group_stage"]["third_place_ranking"],
        "knockout_rounds": knockout_rounds,
        "golden_boot": golden_boot,
        "tournament_mvp": tournament_mvp,
        "top_scorers": top_scorers[:20],
        "mvp_leaderboard": mvp_leaderboard[:20],
        "methodology": "One simulated tournament path. Player goals are distributed by scorer weights from xG/90, goals/90, shots/90, expected minutes, position and role flags. MVP uses goals, assists, knockout goals and team progression bonuses.",
    }
