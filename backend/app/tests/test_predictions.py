import random

from app.predictions.goal_types import predict_goal_types
from app.predictions.match import predict_match
from app.predictions.scorers import predict_scorers
from app.predictions.tournament import generate_group_fixtures, groups_from_teams, simulate_group_stage, simulate_single_tournament, simulate_tournament
from app.services import demo_data


def test_match_prediction_probabilities_sum_close_to_one() -> None:
    prediction = predict_match(
        1,
        demo_data.team_by_id(1),
        demo_data.team_by_id(2),
        demo_data.TEAM_RATINGS[1],
        demo_data.TEAM_RATINGS[2],
    )
    total = (
        prediction["team_a_win_probability"]
        + prediction["draw_probability"]
        + prediction["team_b_win_probability"]
    )
    assert abs(total - 1.0) < 0.01
    assert prediction["most_likely_scorelines"]


def test_tournament_simulation_output_shape() -> None:
    simulation = simulate_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, runs=200)
    assert simulation["simulation_runs"] == 200
    assert len(simulation["teams"]) == 48
    assert {"team", "winner_probability", "final_probability", "round_of_32_probability"}.issubset(simulation["teams"][0])
    assert max(team["quarter_final_probability"] for team in simulation["teams"]) < 1.0


def test_demo_tournament_structure() -> None:
    groups = groups_from_teams(demo_data.TEAMS)
    fixtures = generate_group_fixtures(demo_data.TEAMS)
    assert len(demo_data.TEAMS) == 48
    assert len(groups) == 12
    assert all(len(teams) == 4 for teams in groups.values())
    assert len(fixtures) == 72
    assert all(len([fixture for fixture in fixtures if fixture["group"] == group]) == 6 for group in groups)


def test_group_stage_qualification_logic() -> None:
    group_stage = simulate_group_stage(demo_data.TEAMS, demo_data.TEAM_RATINGS, random.Random(7))
    assert len(group_stage["automatic_qualifiers"]) == 24
    assert len(group_stage["third_place_ranking"]) == 12
    assert len(group_stage["selected_third_place_qualifiers"]) == 8
    assert len(group_stage["qualifiers"]) == 32
    for rows in group_stage["group_tables"].values():
        assert rows[0]["points"] >= rows[1]["points"] or rows[0]["goal_difference"] >= rows[1]["goal_difference"]


def test_single_tournament_produces_one_winner_and_round_of_32() -> None:
    single = simulate_single_tournament(demo_data.TEAMS, demo_data.TEAM_RATINGS, seed=11)
    assert len(single["reached"]["round_of_32"]) == 32
    assert len(single["reached"]["winner"]) == 1
    assert single["winner_id"] == single["reached"]["winner"][0]


def test_scorer_prediction_output() -> None:
    candidates = predict_scorers(demo_data.team_by_id(1), demo_data.players_for_team(1), 1.4)
    assert candidates[0]["probability"] >= candidates[-1]["probability"]
    assert candidates[0]["confidence"] in {"Low", "Medium", "High"}
    assert {"player_name", "team_name", "team_code", "position", "role", "probability", "top_factor", "features"}.issubset(candidates[0])


def test_player_profiles_load_real_names() -> None:
    assert demo_data.PLAYERS
    top_team_codes = {"ARG", "FRA", "ENG", "BRA", "POR", "ESP", "NED", "MAR"}
    for team in demo_data.TEAMS:
        players = demo_data.players_for_team(team["id"])
        if team["country_code"] in top_team_codes:
            assert len(players) >= 8
        assert all(player["name"] for player in players)


def test_scorer_candidates_use_named_player_profiles() -> None:
    candidates = []
    for team in demo_data.TEAMS:
        candidates.extend(predict_scorers(team, demo_data.players_for_team(team["id"]), 1.2))
    names = {candidate["player_name"] for candidate in candidates}
    assert all(name.strip() for name in names)
    assert len(names) > 48
    assert all(candidate["position"] != "GK" for candidate in candidates)


def test_goal_type_prediction_output() -> None:
    output = predict_goal_types(
        demo_data.team_by_id(8),
        demo_data.team_by_id(1),
        demo_data.TEAM_RATINGS[8],
        demo_data.TEAM_RATINGS[1],
        5,
    )
    assert output["team"] == "Morocco"
    assert 0 <= output["set_piece_goal_probability"] <= 1
