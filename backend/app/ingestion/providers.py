from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.services import demo_data


class FootballDataProvider(ABC):
    @abstractmethod
    def get_fixtures(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_match_events(self, match_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_lineups(self, match_id: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_player_stats(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_team_stats(self) -> dict[int, dict[str, float]]:
        raise NotImplementedError

    @abstractmethod
    def get_standings(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class MockWorldCupDataProvider(FootballDataProvider):
    def get_fixtures(self) -> list[dict[str, Any]]:
        return demo_data.MATCHES

    def get_match_events(self, match_id: int) -> list[dict[str, Any]]:
        return demo_data.events_for_match(match_id)

    def get_lineups(self, match_id: int) -> list[dict[str, Any]]:
        match = demo_data.match_by_id(match_id)
        return demo_data.players_for_team(match["home_team_id"]) + demo_data.players_for_team(match["away_team_id"])

    def get_player_stats(self) -> list[dict[str, Any]]:
        return demo_data.PLAYERS

    def get_team_stats(self) -> dict[int, dict[str, float]]:
        return demo_data.TEAM_RATINGS

    def get_standings(self) -> list[dict[str, Any]]:
        return demo_data.TEAMS


class StatsBombOpenDataProvider(MockWorldCupDataProvider):
    """Placeholder adapter for StatsBomb Open Data-style JSON files.

    The MVP uses the same normalized shape as the mock provider. A future
    implementation can parse local StatsBomb JSON into this interface without
    changing the analytics or prediction services.
    """


class ApiFootballProvider(FootballDataProvider):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def _not_configured(self) -> list[dict[str, Any]]:
        return []

    def get_fixtures(self) -> list[dict[str, Any]]:
        return self._not_configured()

    def get_match_events(self, match_id: int) -> list[dict[str, Any]]:
        return self._not_configured()

    def get_lineups(self, match_id: int) -> list[dict[str, Any]]:
        return self._not_configured()

    def get_player_stats(self) -> list[dict[str, Any]]:
        return self._not_configured()

    def get_team_stats(self) -> dict[int, dict[str, float]]:
        return {}

    def get_standings(self) -> list[dict[str, Any]]:
        return self._not_configured()
