from app.analytics.match import calculate_match_analytics, possession_chains, shot_map
from app.services import demo_data


def test_match_analytics_calculates_core_metrics() -> None:
    match = demo_data.match_by_id(1)
    analytics = calculate_match_analytics(
        demo_data.events_for_match(1),
        [match["home_team_id"], match["away_team_id"]],
    )

    argentina = analytics["teams"][1]
    assert argentina["total_shots"] == 9
    assert argentina["set_piece_shots"] >= 1
    assert argentina["xg"] > 0


def test_shot_map_shape() -> None:
    points = shot_map(
        demo_data.events_for_match(1),
        {team["id"]: team["name"] for team in demo_data.TEAMS},
        {player["id"]: player["name"] for player in demo_data.PLAYERS},
    )

    assert points
    assert {"x", "y", "player", "team", "minute", "shot_outcome", "xg"}.issubset(points[0])


def test_possession_chain_shape() -> None:
    chains = possession_chains(demo_data.events_for_match(1))
    assert chains
    assert {"possession_length", "number_of_passes", "start_zone", "end_zone"}.issubset(chains[0])
