from app.predictions.single_tournament import run_single_tournament


def test_single_simulation_returns_one_winner_and_final() -> None:
    result = run_single_tournament(seed=12345)

    assert result["winner"]["name"]
    assert result["runner_up"]["name"]
    assert result["winner"]["name"] != result["runner_up"]["name"]
    assert result["final"]["team_a"]
    assert result["final"]["team_b"]
    assert result["final"]["team_a"] != result["final"]["team_b"]
    assert result["final"]["score"]


def test_single_simulation_awards_have_real_player_names() -> None:
    result = run_single_tournament(seed=12345)

    assert result["golden_boot"]["player_name"]
    assert result["tournament_mvp"]["player_name"]
    assert result["golden_boot"]["player_name"].strip()
    assert result["tournament_mvp"]["player_name"].strip()


def test_single_simulation_same_seed_is_deterministic() -> None:
    first = run_single_tournament(seed=2026)
    second = run_single_tournament(seed=2026)

    assert first["winner"]["name"] == second["winner"]["name"]
    assert first["final"] == second["final"]
    assert first["golden_boot"]["player_name"] == second["golden_boot"]["player_name"]


def test_single_simulation_different_seed_can_change_output() -> None:
    first = run_single_tournament(seed=2026)
    second = run_single_tournament(seed=2027)

    assert (
        first["winner"]["name"] != second["winner"]["name"]
        or first["final"] != second["final"]
        or first["golden_boot"]["player_name"] != second["golden_boot"]["player_name"]
    )
