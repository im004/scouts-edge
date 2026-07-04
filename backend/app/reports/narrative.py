from __future__ import annotations

from typing import Any


class ReportNarrativeService:
    """Rule-based narrative generator that only summarizes supplied metrics."""

    def generate(
        self,
        match: dict[str, Any],
        analytics: dict[str, Any],
        prediction: dict[str, Any],
        scorers: dict[str, Any],
        goal_types: dict[str, Any],
    ) -> str:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        top_score = prediction["most_likely_scorelines"][0]["score"]
        home_metrics = analytics["teams"].get(match["home_team_id"], {})
        away_metrics = analytics["teams"].get(match["away_team_id"], {})
        top_scorers = scorers["candidates"][:3]
        scorer_lines = "\n".join(
            f"- {item['player']} ({item['team']}): {item['anytime_scorer_probability']:.0%} anytime estimate"
            for item in top_scorers
        )
        return f"""# {home} vs {away} Scouting Report

## Match Overview
Stage: {match['stage']}
Venue: {match.get('venue') or 'TBC'}

## Tactical Metrics
- {home}: {home_metrics.get('total_shots', 0)} shots, {home_metrics.get('xg', 0)} xG, {home_metrics.get('dangerous_actions', 0)} dangerous actions.
- {away}: {away_metrics.get('total_shots', 0)} shots, {away_metrics.get('xg', 0)} xG, {away_metrics.get('dangerous_actions', 0)} dangerous actions.

## Prediction Summary
The transparent Poisson-style reference model estimates {home} win {prediction['team_a_win_probability']:.0%}, draw {prediction['draw_probability']:.0%}, and {away} win {prediction['team_b_win_probability']:.0%}. The most likely scoreline is {top_score}.

## Likely Scorer Candidates
{scorer_lines}

## Goal-Type Threat
The model provides separate open-play, set-piece, penalty and counterattack estimates for each team. These are scouting indicators, not betting advice.

## Limitations
This report is generated from deterministic backend metrics and seeded model features. It does not invent unavailable injuries, private training information, or live team news.
"""
