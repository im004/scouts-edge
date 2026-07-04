from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any

from app.predictions.match import expected_goals, predict_match

STAGES = ["group_stage", "round_of_32", "round_of_16", "quarter_final", "semi_final", "final", "winner"]
ROUND_LABELS = [
    ("Round of 32", "round_of_16"),
    ("Round of 16", "quarter_final"),
    ("Quarter-final", "semi_final"),
    ("Semi-final", "final"),
    ("Final", "winner"),
]
GROUP_PAIRINGS = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]


def groups_from_teams(teams: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for team in teams:
        groups[team["group"]].append(team)
    return {group: sorted(group_teams, key=lambda item: item["id"]) for group, group_teams in sorted(groups.items())}


def generate_group_fixtures(teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    fixture_id = 1
    for group, group_teams in groups_from_teams(teams).items():
        for home_index, away_index in GROUP_PAIRINGS:
            home = group_teams[home_index]
            away = group_teams[away_index]
            fixtures.append(
                {
                    "id": fixture_id,
                    "group": group,
                    "stage": "Group Stage",
                    "home_team_id": home["id"],
                    "away_team_id": away["id"],
                    "home_team": home["name"],
                    "away_team": away["name"],
                }
            )
            fixture_id += 1
    return fixtures


def _poisson(k: int, lam: float) -> float:
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def _sample_poisson(rng: random.Random, lam: float, max_goals: int = 7) -> int:
    probabilities = [_poisson(goals, lam) for goals in range(max_goals + 1)]
    total = sum(probabilities)
    draw = rng.random()
    cumulative = 0.0
    for goals, probability in enumerate(probabilities):
        cumulative += probability / total
        if draw <= cumulative:
            return goals
    return max_goals


def _blank_row(team: dict[str, Any]) -> dict[str, Any]:
    return {
        "team_id": team["id"],
        "team": team["name"],
        "group": team["group"],
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "points": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "base_rating": team["base_elo_like_rating"],
    }


def _sort_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            row["points"],
            row["goal_difference"],
            row["goals_for"],
            row["base_rating"],
            -row["team_id"],
        ),
        reverse=True,
    )


def _record_group_result(table: dict[int, dict[str, Any]], home_id: int, away_id: int, home_goals: int, away_goals: int) -> None:
    home = table[home_id]
    away = table[away_id]
    home["played"] += 1
    away["played"] += 1
    home["goals_for"] += home_goals
    home["goals_against"] += away_goals
    away["goals_for"] += away_goals
    away["goals_against"] += home_goals
    home["goal_difference"] = home["goals_for"] - home["goals_against"]
    away["goal_difference"] = away["goals_for"] - away["goals_against"]

    if home_goals > away_goals:
        home["wins"] += 1
        away["losses"] += 1
        home["points"] += 3
    elif away_goals > home_goals:
        away["wins"] += 1
        home["losses"] += 1
        away["points"] += 3
    else:
        home["draws"] += 1
        away["draws"] += 1
        home["points"] += 1
        away["points"] += 1


def simulate_group_stage(
    teams: list[dict[str, Any]],
    ratings: dict[int, dict[str, float]],
    rng: random.Random,
) -> dict[str, Any]:
    group_tables: dict[str, list[dict[str, Any]]] = {}
    match_results: list[dict[str, Any]] = []
    automatic_qualifiers: list[dict[str, Any]] = []
    third_place_rows: list[dict[str, Any]] = []

    for group, group_teams in groups_from_teams(teams).items():
        table = {team["id"]: _blank_row(team) for team in group_teams}
        for home_index, away_index in GROUP_PAIRINGS:
            home = group_teams[home_index]
            away = group_teams[away_index]
            home_xg = expected_goals(ratings[home["id"]], ratings[away["id"]])
            away_xg = expected_goals(ratings[away["id"]], ratings[home["id"]])
            home_goals = _sample_poisson(rng, home_xg)
            away_goals = _sample_poisson(rng, away_xg)
            _record_group_result(table, home["id"], away["id"], home_goals, away_goals)
            match_results.append(
                {
                    "stage": "Group Stage",
                    "group": group,
                    "home_team": home["name"],
                    "away_team": away["name"],
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "home_expected_goals": home_xg,
                    "away_expected_goals": away_xg,
                }
            )
        sorted_rows = _sort_table(list(table.values()))
        for rank, row in enumerate(sorted_rows, start=1):
            row["rank"] = rank
        group_tables[group] = sorted_rows
        automatic_qualifiers.extend(sorted_rows[:2])
        third_place_rows.append(sorted_rows[2])

    third_place_ranking = _sort_table(third_place_rows)
    selected_third_place = third_place_ranking[:8]
    selected_ids = {row["team_id"] for row in selected_third_place}
    qualifier_rows = automatic_qualifiers + selected_third_place
    eliminated = [
        row
        for rows in group_tables.values()
        for row in rows
        if row["rank"] == 4 or (row["rank"] == 3 and row["team_id"] not in selected_ids)
    ]

    return {
        "group_tables": group_tables,
        "group_match_results": match_results,
        "automatic_qualifiers": automatic_qualifiers,
        "third_place_ranking": third_place_ranking,
        "selected_third_place_qualifiers": selected_third_place,
        "eliminated_teams": eliminated,
        "qualifiers": qualifier_rows,
    }


def _team_by_id(teams: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {team["id"]: team for team in teams}


def _winner_probability(team_a: dict[str, Any], team_b: dict[str, Any], ratings: dict[int, dict[str, float]]) -> float:
    prediction = predict_match(0, team_a, team_b, ratings[team_a["id"]], ratings[team_b["id"]])
    decisive = prediction["team_a_win_probability"] + prediction["team_b_win_probability"]
    return prediction["team_a_win_probability"] / decisive if decisive else 0.5


def _simulate_knockout_match(
    stage: str,
    team_a: dict[str, Any],
    team_b: dict[str, Any],
    ratings: dict[int, dict[str, float]],
    rng: random.Random,
) -> dict[str, Any]:
    team_a_xg = expected_goals(ratings[team_a["id"]], ratings[team_b["id"]])
    team_b_xg = expected_goals(ratings[team_b["id"]], ratings[team_a["id"]])
    team_a_goals = _sample_poisson(rng, team_a_xg)
    team_b_goals = _sample_poisson(rng, team_b_xg)
    decided_by = "normal_time"

    if team_a_goals > team_b_goals:
        winner, loser = team_a, team_b
    elif team_b_goals > team_a_goals:
        winner, loser = team_b, team_a
    else:
        decided_by = "penalties"
        winner = team_a if rng.random() < _winner_probability(team_a, team_b, ratings) else team_b
        loser = team_b if winner["id"] == team_a["id"] else team_a

    return {
        "stage": stage,
        "team_a": team_a["name"],
        "team_b": team_b["name"],
        "team_a_goals": team_a_goals,
        "team_b_goals": team_b_goals,
        "team_a_expected_goals": team_a_xg,
        "team_b_expected_goals": team_b_xg,
        "winner": winner["name"],
        "winner_id": winner["id"],
        "loser": loser["name"],
        "loser_id": loser["id"],
        "decided_by": decided_by,
    }


def build_round_of_32(qualifier_rows: list[dict[str, Any]], teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    team_lookup = _team_by_id(teams)
    seeded = sorted(
        qualifier_rows,
        key=lambda row: (row["rank"], -row["points"], -row["goal_difference"], -row["goals_for"], -row["base_rating"], row["team_id"]),
    )
    ordered = [team_lookup[row["team_id"]] for row in seeded]
    bracket: list[dict[str, Any]] = []
    for index in range(16):
        bracket.append({"team_a": ordered[index], "team_b": ordered[-(index + 1)]})
    return bracket


def simulate_knockout(
    qualifier_rows: list[dict[str, Any]],
    teams: list[dict[str, Any]],
    ratings: dict[int, dict[str, float]],
    rng: random.Random,
) -> dict[str, Any]:
    current_pairs = build_round_of_32(qualifier_rows, teams)
    bracket: dict[str, list[dict[str, Any]]] = {}
    reached: dict[str, list[int]] = {stage: [] for stage in STAGES}

    for pairing in current_pairs:
        reached["round_of_32"].extend([pairing["team_a"]["id"], pairing["team_b"]["id"]])

    for stage, next_stage in ROUND_LABELS:
        matches: list[dict[str, Any]] = []
        winners: list[dict[str, Any]] = []
        for pairing in current_pairs:
            result = _simulate_knockout_match(stage, pairing["team_a"], pairing["team_b"], ratings, rng)
            matches.append(result)
            winner = _team_by_id(teams)[result["winner_id"]]
            winners.append(winner)
            reached[next_stage].append(winner["id"])
        bracket[stage] = matches
        if len(winners) == 1:
            break
        current_pairs = [{"team_a": winners[index], "team_b": winners[index + 1]} for index in range(0, len(winners), 2)]

    return {"bracket": bracket, "reached": reached, "winner_id": reached["winner"][0]}


def simulate_single_tournament(
    teams: list[dict[str, Any]],
    ratings: dict[int, dict[str, float]],
    seed: int = 7,
) -> dict[str, Any]:
    rng = random.Random(seed)
    group_stage = simulate_group_stage(teams, ratings, rng)
    knockout = simulate_knockout(group_stage["qualifiers"], teams, ratings, rng)
    winner = _team_by_id(teams)[knockout["winner_id"]]
    return {
        "mode": "full_tournament_demo_seeded",
        "format": "48 teams, 12 groups of 4, top 2 plus 8 best third-place teams, Round of 32 to final",
        "group_stage": group_stage,
        "bracket": knockout["bracket"],
        "winner": winner["name"],
        "winner_id": winner["id"],
        "reached": knockout["reached"],
    }


def simulate_tournament(
    teams: list[dict[str, Any]],
    ratings: dict[int, dict[str, float]],
    runs: int = 1000,
    seed: int = 7,
) -> dict[str, Any]:
    runs = min(max(runs, 100), 10000)
    aggregate: dict[int, dict[str, float]] = {
        team["id"]: {
            "group_stage": runs,
            "round_of_32": 0,
            "round_of_16": 0,
            "quarter_final": 0,
            "semi_final": 0,
            "final": 0,
            "winner": 0,
            "points": 0,
            "goals_for": 0,
            "goals_against": 0,
        }
        for team in teams
    }
    latest_single: dict[str, Any] | None = None

    for run_index in range(runs):
        single = simulate_single_tournament(teams, ratings, seed + run_index)
        latest_single = single
        for rows in single["group_stage"]["group_tables"].values():
            for row in rows:
                stats = aggregate[row["team_id"]]
                stats["points"] += row["points"]
                stats["goals_for"] += row["goals_for"]
                stats["goals_against"] += row["goals_against"]
        for stage in ["round_of_32", "round_of_16", "quarter_final", "semi_final", "final", "winner"]:
            for team_id in single["reached"][stage]:
                aggregate[team_id][stage] += 1

    output = []
    team_lookup = _team_by_id(teams)
    for team_id, counts in aggregate.items():
        team = team_lookup[team_id]
        output.append(
            {
                "team_id": team_id,
                "team": team["name"],
                "group": team["group"],
                "group_stage_probability": 1.0,
                "round_of_32_probability": round(counts["round_of_32"] / runs, 3),
                "round_of_16_probability": round(counts["round_of_16"] / runs, 3),
                "quarter_final_probability": round(counts["quarter_final"] / runs, 3),
                "semi_final_probability": round(counts["semi_final"] / runs, 3),
                "final_probability": round(counts["final"] / runs, 3),
                "winner_probability": round(counts["winner"] / runs, 3),
                "average_points": round(counts["points"] / runs, 2),
                "average_goals_for": round(counts["goals_for"] / runs, 2),
                "average_goals_against": round(counts["goals_against"] / runs, 2),
            }
        )

    assert latest_single is not None
    return {
        "mode": "full_tournament_demo_seeded",
        "simulation_runs": runs,
        "teams": sorted(output, key=lambda item: item["winner_probability"], reverse=True),
        "group_tables": latest_single["group_stage"]["group_tables"],
        "third_place_ranking": latest_single["group_stage"]["third_place_ranking"],
        "selected_third_place_qualifiers": latest_single["group_stage"]["selected_third_place_qualifiers"],
        "eliminated_teams": latest_single["group_stage"]["eliminated_teams"],
        "bracket": latest_single["bracket"],
        "winner": latest_single["winner"],
        "format": latest_single["format"],
    }
