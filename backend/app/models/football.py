from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Competition(Base, TimestampMixin):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(80))
    provider_ref: Mapped[str | None] = mapped_column(String(120), index=True)

    seasons: Mapped[list["Season"]] = relationship(back_populates="competition")


class Season(Base, TimestampMixin):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    year: Mapped[int | None] = mapped_column(Integer)

    competition: Mapped[Competition] = relationship(back_populates="seasons")
    matches: Mapped[list["Match"]] = relationship(back_populates="season")

    __table_args__ = (UniqueConstraint("competition_id", "name", name="uq_season_competition_name"),)


class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    short_name: Mapped[str] = mapped_column(String(16), index=True)
    country: Mapped[str | None] = mapped_column(String(80))
    fifa_rank: Mapped[int | None] = mapped_column(Integer)
    provider_ref: Mapped[str | None] = mapped_column(String(120), index=True)

    players: Mapped[list["Player"]] = relationship(back_populates="team")
    rating: Mapped["TeamRating | None"] = relationship(back_populates="team", uselist=False)


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    name: Mapped[str] = mapped_column(String(140), index=True)
    position: Mapped[str | None] = mapped_column(String(40))
    shirt_number: Mapped[int | None] = mapped_column(Integer)
    provider_ref: Mapped[str | None] = mapped_column(String(120), index=True)

    team: Mapped[Team] = relationship(back_populates="players")
    rating_features: Mapped["PlayerRatingFeature | None"] = relationship(back_populates="player", uselist=False)

    __table_args__ = (UniqueConstraint("team_id", "name", name="uq_player_team_name"),)


class Match(Base, TimestampMixin):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int | None] = mapped_column(ForeignKey("seasons.id"), index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    match_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    stage: Mapped[str] = mapped_column(String(80), default="Group Stage")
    venue: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="scheduled", index=True)
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    provider_ref: Mapped[str | None] = mapped_column(String(120), index=True)

    season: Mapped["Season | None"] = relationship(back_populates="matches")
    home_team: Mapped[Team] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped[Team] = relationship(foreign_keys=[away_team_id])
    events: Mapped[list["Event"]] = relationship(back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_matches_teams_date", "home_team_id", "away_team_id", "match_date"),)


class Lineup(Base, TimestampMixin):
    __tablename__ = "lineups"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    is_starting: Mapped[bool] = mapped_column(Boolean, default=False)
    expected_minutes: Mapped[float] = mapped_column(Float, default=60.0)


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"), index=True)
    minute: Mapped[int] = mapped_column(Integer, index=True)
    second: Mapped[int] = mapped_column(Integer, default=0)
    event_type: Mapped[str] = mapped_column(String(60), index=True)
    play_pattern: Mapped[str | None] = mapped_column(String(80), index=True)
    possession_id: Mapped[int | None] = mapped_column(Integer, index=True)
    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)
    end_x: Mapped[float | None] = mapped_column(Float)
    end_y: Mapped[float | None] = mapped_column(Float)
    outcome: Mapped[str | None] = mapped_column(String(80))
    body_part: Mapped[str | None] = mapped_column(String(40))
    xg: Mapped[float | None] = mapped_column(Float)
    raw: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    match: Mapped[Match] = relationship(back_populates="events")
    team: Mapped[Team] = relationship()
    player: Mapped["Player | None"] = relationship()

    __table_args__ = (Index("ix_events_match_type_minute", "match_id", "event_type", "minute"),)


class Shot(Base, TimestampMixin):
    __tablename__ = "shots"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), unique=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"), index=True)
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    outcome: Mapped[str | None] = mapped_column(String(80))
    xg: Mapped[float | None] = mapped_column(Float)
    play_pattern: Mapped[str | None] = mapped_column(String(80))
    body_part: Mapped[str | None] = mapped_column(String(40))


class Possession(Base, TimestampMixin):
    __tablename__ = "possessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    provider_possession_id: Mapped[int | None] = mapped_column(Integer, index=True)
    start_minute: Mapped[int] = mapped_column(Integer)
    end_minute: Mapped[int] = mapped_column(Integer)
    start_zone: Mapped[str | None] = mapped_column(String(40))
    end_zone: Mapped[str | None] = mapped_column(String(40))
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    pass_count: Mapped[int] = mapped_column(Integer, default=0)
    ended_with_shot: Mapped[bool] = mapped_column(Boolean, default=False)
    ended_with_turnover: Mapped[bool] = mapped_column(Boolean, default=False)
    directness: Mapped[float] = mapped_column(Float, default=0.0)


class TeamMatchStat(Base, TimestampMixin):
    __tablename__ = "team_match_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    __table_args__ = (UniqueConstraint("match_id", "team_id", name="uq_team_match_stats"),)


class PlayerMatchStat(Base, TimestampMixin):
    __tablename__ = "player_match_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    __table_args__ = (UniqueConstraint("match_id", "player_id", name="uq_player_match_stats"),)


class TeamRating(Base, TimestampMixin):
    __tablename__ = "team_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), unique=True, index=True)
    base_rating: Mapped[float] = mapped_column(Float)
    attack_strength: Mapped[float] = mapped_column(Float)
    defence_strength: Mapped[float] = mapped_column(Float)
    recent_form: Mapped[float] = mapped_column(Float)
    goals_scored: Mapped[float] = mapped_column(Float, default=0.0)
    goals_conceded: Mapped[float] = mapped_column(Float, default=0.0)
    xg_for: Mapped[float | None] = mapped_column(Float)
    xg_against: Mapped[float | None] = mapped_column(Float)
    set_piece_threat: Mapped[float] = mapped_column(Float, default=0.5)
    set_piece_weakness: Mapped[float] = mapped_column(Float, default=0.5)
    open_play_threat: Mapped[float] = mapped_column(Float, default=0.5)
    competition_strength: Mapped[float] = mapped_column(Float, default=1.0)

    team: Mapped[Team] = relationship(back_populates="rating")


class PlayerRatingFeature(Base, TimestampMixin):
    __tablename__ = "player_rating_features"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), unique=True, index=True)
    expected_minutes: Mapped[float] = mapped_column(Float, default=60.0)
    goals_per_90: Mapped[float] = mapped_column(Float, default=0.0)
    shots_per_90: Mapped[float] = mapped_column(Float, default=0.0)
    xg_per_90: Mapped[float] = mapped_column(Float, default=0.0)
    penalty_taker: Mapped[bool] = mapped_column(Boolean, default=False)
    set_piece_target: Mapped[bool] = mapped_column(Boolean, default=False)
    starting_probability: Mapped[float] = mapped_column(Float, default=0.7)
    recent_form: Mapped[float] = mapped_column(Float, default=0.5)

    player: Mapped[Player] = relationship(back_populates="rating_features")


class MatchPrediction(Base, TimestampMixin):
    __tablename__ = "match_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class TournamentSimulation(Base, TimestampMixin):
    __tablename__ = "tournament_simulations"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_runs: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class ScorerPrediction(Base, TimestampMixin):
    __tablename__ = "scorer_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class GoalTypePrediction(Base, TimestampMixin):
    __tablename__ = "goal_type_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class GeneratedReport(Base, TimestampMixin):
    __tablename__ = "generated_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    format: Mapped[str] = mapped_column(String(20), default="markdown")
    content: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
