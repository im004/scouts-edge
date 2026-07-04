from __future__ import annotations

from collections import defaultdict
from typing import Any

SET_PIECE_PATTERNS = {"From Corner", "From Free Kick", "From Throw In"}
SHOT_OUTCOMES_ON_TARGET = {"Goal", "Saved", "Saved to Post"}


def _zone(x: float | None) -> str:
    if x is None:
        return "unknown"
    if x < 40:
        return "defensive third"
    if x < 80:
        return "middle third"
    if x < 102:
        return "final third"
    return "penalty area"


def calculate_match_analytics(events: list[dict[str, Any]], team_ids: list[int]) -> dict[str, Any]:
    metrics: dict[int, dict[str, Any]] = {}
    total_events = max(len(events), 1)

    for team_id in team_ids:
        team_events = [event for event in events if event["team_id"] == team_id]
        shots = [event for event in team_events if event["event_type"] == "Shot"]
        passes = [event for event in team_events if event["event_type"] == "Pass"]
        dangerous = [
            event
            for event in team_events
            if (event.get("x") or 0) >= 90 or event["event_type"] in {"Shot", "Corner", "Free Kick"}
        ]
        set_piece_shots = [shot for shot in shots if shot.get("play_pattern") in SET_PIECE_PATTERNS]
        open_play_shots = [shot for shot in shots if shot.get("play_pattern") not in SET_PIECE_PATTERNS]
        passes_into_area = [
            event
            for event in passes
            if (event.get("end_x") or 0) >= 102 and 18 <= (event.get("end_y") or 0) <= 62
        ]
        final_third_entries = [
            event
            for event in team_events
            if (event.get("end_x") or event.get("x") or 0) >= 80 and (event.get("x") or 0) < 80
        ]
        box_entries = [
            event
            for event in team_events
            if (event.get("end_x") or event.get("x") or 0) >= 102 and 18 <= (event.get("end_y") or event.get("y") or 0) <= 62
        ]
        counter_events = [event for event in team_events if event.get("play_pattern") == "Counter"]
        xg = round(sum(float(shot.get("xg") or 0.0) for shot in shots), 2)
        set_piece_xg = round(sum(float(shot.get("xg") or 0.0) for shot in set_piece_shots), 2)
        goals = len([shot for shot in shots if shot.get("outcome") == "Goal"])
        set_piece_goals = len([shot for shot in set_piece_shots if shot.get("outcome") == "Goal"])

        metrics[team_id] = {
            "total_shots": len(shots),
            "shots_on_target": len([shot for shot in shots if shot.get("outcome") in SHOT_OUTCOMES_ON_TARGET]),
            "xg": xg,
            "possession_proxy": round(len(team_events) / total_events, 3),
            "final_third_entries": len(final_third_entries),
            "box_entries": len(box_entries),
            "dangerous_actions": len(dangerous),
            "set_piece_shots": len(set_piece_shots),
            "open_play_shots": len(open_play_shots),
            "counterattack_events": len(counter_events),
            "passes_into_penalty_area": len(passes_into_area),
            "progressive_passes": len([event for event in passes if (event.get("end_x") or 0) - (event.get("x") or 0) >= 20]),
            "defensive_actions": len([event for event in team_events if event["event_type"] in {"Pressure", "Tackle", "Interception", "Block"}]),
            "corners": len([event for event in team_events if event["event_type"] == "Corner"]),
            "free_kicks": len([event for event in team_events if event["event_type"] == "Free Kick"]),
            "throw_ins": len([event for event in team_events if event["event_type"] == "Throw In"]),
            "set_piece_xg": set_piece_xg,
            "set_piece_goal_share": round(set_piece_goals / goals, 3) if goals else 0.0,
            "set_piece_threat_score": round(min(1.0, (len(set_piece_shots) * 0.18) + (set_piece_xg * 0.7)), 3),
        }

    return {"teams": metrics}


def shot_map(events: list[dict[str, Any]], teams: dict[int, str], players: dict[int, str]) -> list[dict[str, Any]]:
    return [
        {
            "x": event.get("x"),
            "y": event.get("y"),
            "player": players.get(event.get("player_id"), "Unknown"),
            "team": teams.get(event["team_id"], "Unknown"),
            "minute": event["minute"],
            "shot_outcome": event.get("outcome"),
            "xg": event.get("xg"),
            "body_part": event.get("body_part"),
            "play_pattern": event.get("play_pattern"),
        }
        for event in events
        if event["event_type"] == "Shot"
    ]


def possession_chains(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped[(event["team_id"], event.get("possession_id") or event["id"])].append(event)

    chains: list[dict[str, Any]] = []
    for (team_id, possession_id), chain_events in grouped.items():
        ordered = sorted(chain_events, key=lambda event: (event["minute"], event.get("second", 0)))
        first = ordered[0]
        last = ordered[-1]
        start_x = first.get("x")
        end_x = last.get("end_x") if last.get("end_x") is not None else last.get("x")
        duration = max(1, last["minute"] - first["minute"] + 1)
        chains.append(
            {
                "team_id": team_id,
                "possession_id": possession_id,
                "possession_length": len(ordered),
                "number_of_passes": len([event for event in ordered if event["event_type"] == "Pass"]),
                "start_zone": _zone(start_x),
                "end_zone": _zone(end_x),
                "ended_with_shot": any(event["event_type"] == "Shot" for event in ordered),
                "ended_with_turnover": last.get("outcome") in {"Incomplete", "Lost", "Dispossessed"},
                "speed_directness_proxy": round(abs((end_x or start_x or 0) - (start_x or 0)) / duration, 2),
            }
        )
    return chains


def player_involvement(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if event.get("player_id"):
            grouped[event["player_id"]].append(event)
    output: list[dict[str, Any]] = []
    for player_id, player_events in grouped.items():
        shots = len([event for event in player_events if event["event_type"] == "Shot"])
        passes = len([event for event in player_events if event["event_type"] == "Pass"])
        defensive = len([event for event in player_events if event["event_type"] in {"Pressure", "Tackle", "Interception", "Block"}])
        output.append(
            {
                "player_id": player_id,
                "touches_events": len(player_events),
                "shots": shots,
                "key_passes": len([event for event in player_events if event["event_type"] == "Pass" and (event.get("end_x") or 0) >= 102]),
                "carries": len([event for event in player_events if event["event_type"] == "Carry"]),
                "defensive_actions": defensive,
                "involvement_score": round(len(player_events) * 0.4 + shots * 1.4 + passes * 0.2 + defensive * 0.6, 2),
            }
        )
    return sorted(output, key=lambda item: item["involvement_score"], reverse=True)
