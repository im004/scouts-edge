from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scheduled_match_returns_pre_match_preview() -> None:
    response = client.get("/matches/4/analytics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "pre_match"
    assert payload["has_event_data"] is False
    assert "pre_match_preview" in payload
    assert "0 shots" not in payload["pre_match_preview"]["summary"]


def test_empty_shot_map_has_reason() -> None:
    response = client.get("/matches/4/shot-map")
    assert response.status_code == 200
    payload = response.json()
    assert payload["has_shots"] is False
    assert payload["empty_state"]["title"] == "No shot map available yet"


def test_tournament_endpoints() -> None:
    groups = client.get("/tournament/groups").json()["groups"]
    assert len(groups) == 12
    assert all(len(group) == 4 for group in groups.values())

    simulation = client.post("/tournament/simulate", json={"runs": 100, "seed": 7}).json()
    assert simulation["simulation_runs"] == 100
    assert len(simulation["teams"]) == 48
    assert len(simulation["third_place_ranking"]) == 12


def test_scorer_endpoint_returns_real_player_shape() -> None:
    response = client.get("/predictions/scorers/4")
    assert response.status_code == 200
    candidate = response.json()["candidates"][0]
    assert {"player_name", "position", "role", "probability"}.issubset(candidate)
    assert candidate["player_name"].strip()


def test_team_profile_endpoint_returns_named_players() -> None:
    response = client.get("/teams/1")
    assert response.status_code == 200
    players = response.json()["players"]
    assert len(players) >= 8
    assert players[0]["player_name"]
    assert players[0]["player_name"].strip()


def test_single_tournament_run_endpoint() -> None:
    response = client.post("/tournament/simulate/run", json={"seed": 12345, "include_awards": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["winner"]["name"]
    assert payload["final"]["team_a"]
    assert payload["final"]["team_b"]
    assert payload["golden_boot"]["player_name"]
    assert payload["tournament_mvp"]["player_name"]
