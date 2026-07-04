from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal, engine
from app.models.football import Base, Competition, Event, Match, Player, PlayerRatingFeature, Season, Team, TeamRating
from app.services import demo_data


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        competition = db.scalar(select(Competition).where(Competition.name == "FIFA World Cup"))
        if competition is None:
            competition = Competition(name="FIFA World Cup", country="International", provider_ref="demo-world-cup")
            db.add(competition)
            db.flush()

        season = db.scalar(select(Season).where(Season.competition_id == competition.id, Season.name == "2026 Demo"))
        if season is None:
            season = Season(competition_id=competition.id, name="2026 Demo", year=2026)
            db.add(season)
            db.flush()

        team_columns = {"id", "name", "short_name", "country", "fifa_rank"}
        rating_columns = {
            "base_rating",
            "attack_strength",
            "defence_strength",
            "recent_form",
            "goals_scored",
            "goals_conceded",
            "xg_for",
            "xg_against",
            "set_piece_threat",
            "set_piece_weakness",
            "open_play_threat",
            "competition_strength",
        }
        match_columns = {
            "id",
            "home_team_id",
            "away_team_id",
            "match_date",
            "stage",
            "venue",
            "status",
            "home_score",
            "away_score",
        }
        player_columns = {"id", "team_id", "name", "position"}
        player_rating_columns = {
            "expected_minutes",
            "goals_per_90",
            "shots_per_90",
            "xg_per_90",
            "penalty_taker",
            "set_piece_target",
            "starting_probability",
            "recent_form",
        }

        for team_data in demo_data.TEAMS:
            team_payload = {key: value for key, value in team_data.items() if key in team_columns}
            team = db.get(Team, team_payload["id"])
            if team is None:
                team = Team(**team_payload, provider_ref=f"demo-team-{team_payload['id']}")
                db.add(team)
            else:
                for key, value in team_payload.items():
                    setattr(team, key, value)
            db.flush()

            rating_data = {
                key: value
                for key, value in demo_data.TEAM_RATINGS[team_payload["id"]].items()
                if key in rating_columns
            }
            rating = db.scalar(select(TeamRating).where(TeamRating.team_id == team.id))
            if rating is None:
                db.add(TeamRating(team_id=team.id, **rating_data))
            else:
                for key, value in rating_data.items():
                    setattr(rating, key, value)

        for player_data in demo_data.PLAYERS:
            features = {
                key: value
                for key, value in player_data["features"].items()
                if key in player_rating_columns
            }
            player_payload = {key: value for key, value in player_data.items() if key in player_columns}
            player = db.get(Player, player_payload["id"])
            if player is None:
                player = Player(**player_payload, provider_ref=f"demo-player-{player_payload['id']}")
                db.add(player)
            else:
                for key, value in player_payload.items():
                    setattr(player, key, value)
            db.flush()

            rating = db.scalar(select(PlayerRatingFeature).where(PlayerRatingFeature.player_id == player.id))
            if rating is None:
                db.add(PlayerRatingFeature(player_id=player.id, **features))
            else:
                for key, value in features.items():
                    setattr(rating, key, value)

        for match_data in demo_data.MATCHES:
            payload = {
                **{key: value for key, value in match_data.items() if key in match_columns},
                "season_id": season.id,
                "provider_ref": f"demo-match-{match_data['id']}",
            }
            match = db.get(Match, payload["id"])
            if match is None:
                db.add(Match(**payload))
            else:
                for key, value in payload.items():
                    setattr(match, key, value)

        for event_data in demo_data.EVENTS:
            event = db.get(Event, event_data["id"])
            payload = {**event_data, "raw": event_data}
            if event is None:
                db.add(Event(**payload))
            else:
                for key, value in payload.items():
                    setattr(event, key, value)

        db.commit()


if __name__ == "__main__":
    seed()
    print("Seeded demo World Cup teams, players, matches and events.")
