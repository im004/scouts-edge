from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    id: int
    name: str
    short_name: str
    country: str | None = None
    fifa_rank: int | None = None

    model_config = ConfigDict(from_attributes=True)


class MatchOut(BaseModel):
    id: int
    home_team_id: int
    away_team_id: int
    match_date: datetime
    stage: str
    venue: str | None = None
    status: str
    home_score: int | None = None
    away_score: int | None = None
    home_team: dict[str, Any] | None = None
    away_team: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class SimulationRequest(BaseModel):
    runs: int = 1000
    seed: int = 7


class SingleSimulationRunRequest(BaseModel):
    seed: int | None = None
    include_awards: bool = True


class HealthOut(BaseModel):
    status: str
    service: str
    mode: str
