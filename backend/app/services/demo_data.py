from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.ingestion.squad_importer import load_player_profiles

GROUP_NAMES = [f"Group {letter}" for letter in "ABCDEFGHIJKL"]
DATASET_LABEL = "Demo tournament dataset for engineering purposes, not official FIFA fixture data."
PLAYER_PROFILE_LABEL = "Curated demo player profiles for engineering purposes."

_TEAM_SEEDS: list[tuple[str, str, float]] = [
    ("Argentina", "ARG", 90),
    ("Portugal", "POR", 86),
    ("France", "FRA", 89),
    ("Netherlands", "NED", 84),
    ("England", "ENG", 87),
    ("Brazil", "BRA", 88),
    ("Spain", "ESP", 85),
    ("Morocco", "MAR", 80),
    ("Germany", "GER", 85),
    ("Italy", "ITA", 83),
    ("Belgium", "BEL", 82),
    ("Croatia", "CRO", 81),
    ("Uruguay", "URU", 81),
    ("Colombia", "COL", 80),
    ("Mexico", "MEX", 78),
    ("USA", "USA", 77),
    ("Canada", "CAN", 74),
    ("Japan", "JPN", 78),
    ("South Korea", "KOR", 76),
    ("Senegal", "SEN", 77),
    ("Nigeria", "NGA", 75),
    ("Ghana", "GHA", 73),
    ("Egypt", "EGY", 76),
    ("Tunisia", "TUN", 72),
    ("Algeria", "ALG", 74),
    ("Saudi Arabia", "KSA", 71),
    ("Qatar", "QAT", 69),
    ("Australia", "AUS", 73),
    ("Switzerland", "SUI", 80),
    ("Denmark", "DEN", 79),
    ("Sweden", "SWE", 76),
    ("Norway", "NOR", 77),
    ("Serbia", "SRB", 75),
    ("Poland", "POL", 75),
    ("Austria", "AUT", 77),
    ("Turkey", "TUR", 76),
    ("Wales", "WAL", 72),
    ("Scotland", "SCO", 71),
    ("Chile", "CHI", 73),
    ("Ecuador", "ECU", 75),
    ("Paraguay", "PAR", 72),
    ("Peru", "PER", 72),
    ("Cameroon", "CMR", 73),
    ("Ivory Coast", "CIV", 74),
    ("South Africa", "RSA", 70),
    ("Costa Rica", "CRC", 69),
    ("Panama", "PAN", 68),
    ("New Zealand", "NZL", 67),
]


def _clamp(value: float, low: float = 0.35, high: float = 0.95) -> float:
    return round(max(low, min(high, value)), 3)


def _team_profile(index: int, name: str, code: str, elo: float) -> dict[str, Any]:
    group = GROUP_NAMES[index // 4]
    strength = (elo - 65) / 30
    variation = ((index % 7) - 3) * 0.015
    attack = _clamp(0.52 + strength * 0.34 + variation)
    defence = _clamp(0.54 + strength * 0.30 - variation / 2)
    form = _clamp(0.48 + strength * 0.24 + ((index % 5) - 2) * 0.025)
    set_piece = _clamp(0.44 + strength * 0.20 + ((index % 4) * 0.035))
    weakness = _clamp(0.62 - strength * 0.18 + ((index % 6) - 2) * 0.018)
    open_play = _clamp(0.50 + strength * 0.33 + ((index % 3) - 1) * 0.025)
    counter = _clamp(0.43 + strength * 0.24 + ((index % 8) - 3) * 0.017)
    goalkeeper = _clamp(0.50 + strength * 0.28 + ((index % 6) - 2) * 0.018)
    depth = _clamp(0.48 + strength * 0.30 + ((index % 5) - 2) * 0.02)
    return {
        "id": index + 1,
        "name": name,
        "short_name": code,
        "country": name,
        "country_code": code,
        "group": group,
        "fifa_rank": index + 1,
        "attack_rating": attack,
        "defence_rating": defence,
        "form_rating": form,
        "set_piece_threat": set_piece,
        "set_piece_weakness": weakness,
        "open_play_threat": open_play,
        "counterattack_threat": counter,
        "goalkeeper_rating": goalkeeper,
        "squad_depth": depth,
        "base_elo_like_rating": elo,
    }


TEAMS: list[dict[str, Any]] = [
    _team_profile(index, name, code, elo) for index, (name, code, elo) in enumerate(_TEAM_SEEDS)
]


TEAM_RATINGS: dict[int, dict[str, float]] = {
    team["id"]: {
        "base_rating": team["base_elo_like_rating"],
        "attack_strength": team["attack_rating"],
        "defence_strength": team["defence_rating"],
        "recent_form": team["form_rating"],
        "goals_scored": round(8 + team["attack_rating"] * 16, 1),
        "goals_conceded": round(18 - team["defence_rating"] * 12, 1),
        "xg_for": round(7 + team["attack_rating"] * 14, 1),
        "xg_against": round(16 - team["defence_rating"] * 10, 1),
        "set_piece_threat": team["set_piece_threat"],
        "set_piece_weakness": team["set_piece_weakness"],
        "open_play_threat": team["open_play_threat"],
        "counterattack_threat": team["counterattack_threat"],
        "goalkeeper_rating": team["goalkeeper_rating"],
        "squad_depth": team["squad_depth"],
        "base_elo_like_rating": team["base_elo_like_rating"],
        "competition_strength": 1.0,
    }
    for team in TEAMS
}


def _load_players_from_profiles() -> list[dict[str, Any]]:
    team_by_code = {team["country_code"]: team for team in TEAMS}
    players: list[dict[str, Any]] = []
    for player_id, profile in enumerate(load_player_profiles(), start=1):
        team = team_by_code.get(profile["team_code"])
        if team is None:
            continue
        players.append(
            {
                "id": player_id,
                "team_id": team["id"],
                "name": profile["player_name"],
                "player_name": profile["player_name"],
                "team_name": team["name"],
                "team_code": team["country_code"],
                "position": profile["position"],
                "role": profile["role"],
                "features": {
                    "expected_minutes": profile["expected_minutes"],
                    "starting_probability": profile["starting_probability"],
                    "goals_per_90": profile["goals_per_90"],
                    "shots_per_90": profile["shots_per_90"],
                    "xg_per_90": profile["xg_per_90"],
                    "penalty_taker": profile["penalty_taker"],
                    "set_piece_taker": profile["set_piece_taker"],
                    "set_piece_target": profile["aerial_threat"],
                    "aerial_threat": profile["aerial_threat"],
                    "creative_threat": profile["creative_threat"],
                    "mvp_rating_base": profile["mvp_rating_base"],
                    "recent_form": TEAM_RATINGS[team["id"]]["recent_form"],
                },
                "profile_source": PLAYER_PROFILE_LABEL,
            }
        )
    return players


PLAYERS: list[dict[str, Any]] = _load_players_from_profiles()


_BASE_DATE = datetime(2026, 6, 11, 19, 0)
_PAIRINGS = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]
_COMPLETED_MATCH_IDS = {1, 2, 3, 7, 8, 13, 14, 19}


def group_teams(group_name: str) -> list[dict[str, Any]]:
    return [team for team in TEAMS if team["group"] == group_name]


def generate_group_fixtures() -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    match_id = 1
    for group_index, group_name in enumerate(GROUP_NAMES):
        teams = group_teams(group_name)
        for round_index, (home_index, away_index) in enumerate(_PAIRINGS):
            status = "completed" if match_id in _COMPLETED_MATCH_IDS else "scheduled"
            home_score = away_score = None
            if status == "completed":
                home_score = 1 + ((match_id + home_index) % 3)
                away_score = (match_id + away_index) % 3
            fixtures.append(
                {
                    "id": match_id,
                    "home_team_id": teams[home_index]["id"],
                    "away_team_id": teams[away_index]["id"],
                    "match_date": _BASE_DATE + timedelta(days=group_index * 3 + round_index // 2),
                    "stage": "Group Stage",
                    "group": group_name,
                    "venue": "Offline demo fixture",
                    "status": status,
                    "home_score": home_score,
                    "away_score": away_score,
                }
            )
            match_id += 1
    return fixtures


MATCHES: list[dict[str, Any]] = generate_group_fixtures()


def _players_by_team(team_id: int) -> list[dict[str, Any]]:
    return [player for player in PLAYERS if player["team_id"] == team_id]


def _event(event_id: int, match_id: int, team_id: int, player_id: int, minute: int, event_type: str, **kwargs: Any) -> dict[str, Any]:
    return {
        "id": event_id,
        "match_id": match_id,
        "team_id": team_id,
        "player_id": player_id,
        "minute": minute,
        "second": kwargs.pop("second", 0),
        "event_type": event_type,
        "play_pattern": kwargs.pop("play_pattern", "Regular Play"),
        "possession_id": kwargs.pop("possession_id", event_id),
        **kwargs,
    }


def _generate_match_events(match: dict[str, Any], start_event_id: int) -> list[dict[str, Any]]:
    home_players = _players_by_team(match["home_team_id"])
    away_players = _players_by_team(match["away_team_id"])
    events: list[dict[str, Any]] = []
    event_id = start_event_id
    possession_id = match["id"] * 100
    shot_outcomes = ["Saved", "Off Target", "Blocked", "Goal", "Saved", "Off Target"]

    for shot_index in range(18):
        team_id = match["home_team_id"] if shot_index % 2 == 0 else match["away_team_id"]
        players = home_players if team_id == match["home_team_id"] else away_players
        player = players[shot_index % len(players)]
        minute = 5 + shot_index * 4
        play_pattern = "From Corner" if shot_index in {3, 10, 15} else "Counter" if shot_index in {5, 12} else "Regular Play"
        xg = round(0.05 + (shot_index % 5) * 0.04 + (0.06 if play_pattern == "From Corner" else 0), 2)
        events.append(
            _event(
                event_id,
                match["id"],
                team_id,
                player["id"],
                max(1, minute - 1),
                "Pass" if shot_index % 3 else "Carry",
                possession_id=possession_id,
                x=45 + (shot_index % 6) * 8,
                y=18 + (shot_index % 7) * 6,
                end_x=86 + (shot_index % 4) * 7,
                end_y=22 + (shot_index % 6) * 6,
                outcome="Complete",
                play_pattern=play_pattern,
            )
        )
        event_id += 1
        if play_pattern == "From Corner":
            events.append(
                _event(
                    event_id,
                    match["id"],
                    team_id,
                    players[1]["id"],
                    max(1, minute - 2),
                    "Corner",
                    possession_id=possession_id,
                    x=120,
                    y=0 if shot_index % 2 else 80,
                    end_x=104,
                    end_y=38,
                    outcome="Complete",
                    play_pattern=play_pattern,
                )
            )
            event_id += 1
        events.append(
            _event(
                event_id,
                match["id"],
                team_id,
                player["id"],
                minute,
                "Shot",
                possession_id=possession_id,
                x=93 + (shot_index % 6) * 4,
                y=20 + (shot_index % 8) * 5,
                outcome=shot_outcomes[(shot_index + match["id"]) % len(shot_outcomes)],
                body_part="Head" if play_pattern == "From Corner" else "Right Foot",
                xg=xg,
                play_pattern=play_pattern,
            )
        )
        event_id += 1
        possession_id += 1

    for defensive_index in range(12):
        team_id = match["home_team_id"] if defensive_index % 2 else match["away_team_id"]
        players = home_players if team_id == match["home_team_id"] else away_players
        events.append(
            _event(
                event_id,
                match["id"],
                team_id,
                players[3]["id"],
                12 + defensive_index * 6,
                ["Pressure", "Tackle", "Interception", "Block"][defensive_index % 4],
                possession_id=possession_id + defensive_index,
                x=35 + defensive_index * 3,
                y=15 + defensive_index * 4,
                outcome="Complete",
            )
        )
        event_id += 1
    return events


EVENTS: list[dict[str, Any]] = []
_next_event_id = 1
for _match in MATCHES:
    if _match["status"] == "completed":
        match_events = _generate_match_events(_match, _next_event_id)
        EVENTS.extend(match_events)
        _next_event_id += len(match_events)


def team_by_id(team_id: int) -> dict[str, Any]:
    return next(team for team in TEAMS if team["id"] == team_id)


def match_by_id(match_id: int) -> dict[str, Any]:
    return next(match for match in MATCHES if match["id"] == match_id)


def players_for_team(team_id: int) -> list[dict[str, Any]]:
    return [player for player in PLAYERS if player["team_id"] == team_id]


def events_for_match(match_id: int) -> list[dict[str, Any]]:
    return [event for event in EVENTS if event["match_id"] == match_id]


def has_event_data(match_id: int) -> bool:
    return bool(events_for_match(match_id))


def enriched_match(match: dict[str, Any]) -> dict[str, Any]:
    events = events_for_match(match["id"])
    home_team = team_by_id(match["home_team_id"])
    away_team = team_by_id(match["away_team_id"])
    return {
        **match,
        "home_team": {**home_team, "rating": TEAM_RATINGS[home_team["id"]]},
        "away_team": {**away_team, "rating": TEAM_RATINGS[away_team["id"]]},
        "has_event_data": bool(events),
        "event_count": len(events),
        "dataset_label": DATASET_LABEL,
    }
