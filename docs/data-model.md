# Data Model

The schema is designed around normalized football entities and JSON payload columns for calculated metrics.

## Core Tables

- `competitions`, `seasons`: competition context.
- `teams`, `players`: squad entities with provider references.
- `matches`: fixture metadata, teams, status and score.
- `lineups`: expected or confirmed player involvement.
- `events`: normalized event feed records.
- `shots`: shot-specific event projection.
- `possessions`: possession-chain summaries.
- `team_match_stats`, `player_match_stats`: calculated metrics per match.

The offline demo also exposes API-level tournament metadata such as `group`, `country_code`, `counterattack_threat`, `goalkeeper_rating`, `squad_depth` and `base_elo_like_rating`. These fields are currently generated in the seed service for the demo simulation. A production hardening pass can persist them as first-class columns or a versioned tournament-participant table.

## Prediction Tables

- `team_ratings`: transparent rating inputs such as attack strength, defence strength and recent form.
- `player_rating_features`: scoring model features such as xG per 90 and expected minutes.
- `match_predictions`: stored match probability payloads.
- `tournament_simulations`: Monte Carlo output payloads.
- `scorer_predictions`: player scoring estimate payloads.
- `goal_type_predictions`: open-play, set-piece, penalty and counterattack estimates.

Tournament simulation payloads include group tables, automatic qualifiers, third-place rankings, selected third-place qualifiers, eliminated teams, knockout bracket snapshots and per-team stage probabilities.

## Player Profiles

The demo data layer includes named player profiles in `data/seed/player_profiles.csv`. Profiles provide enough player-level signal for scorer candidates and tournament awards without requiring a paid data feed.

Player profile features include:

- expected minutes and starting probability;
- goals, shots and xG per 90;
- position and role;
- penalty-taker and set-piece-taker flags;
- aerial threat, set-piece target and creative threat;
- base rating used by the tournament MVP model.

The importer is intentionally provider-friendly: current profiles are curated demo seed data, while the schema and service layer can be replaced by official squad lists or a football data API without changing the dashboard contract.

## Report Tables

- `generated_reports`: generated markdown or HTML report content with source payload metadata.
