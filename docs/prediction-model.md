# Prediction Model

The Scout's Edge is not a betting product. It does not provide betting odds, staking advice, bookmaker integrations or gambling recommendations. Predictions are framed as probabilistic football analytics and transparent simulation.

## Team Rating Model

Each team has manually editable or provider-derived inputs:

- base rating
- attack strength
- defence strength
- recent form
- goals scored and conceded
- xG for and against
- set-piece threat and weakness
- open-play threat
- competition strength adjustment

## Match Expected Goals

The model combines team attack strength, opponent defence strength and recent form into expected goals. The formula is deliberately simple so engineers and recruiters can inspect it.

## Poisson-Style Baseline

Expected goals are converted into a grid of scoreline probabilities from 0-0 to 5-5. The grid produces team A win, draw and team B win probabilities plus the most likely scorelines.

This is a transparent Poisson-style baseline, not a calibrated professional forecasting model. It is designed to make assumptions inspectable while still supporting match predictions, Monte Carlo tournament probabilities and single-run tournament paths.

## Tournament Simulation

The tournament model now runs the full 48-team demo format many times:

- 12 groups of 4 teams.
- 6 group-stage fixtures per group.
- Top 2 from each group qualify automatically.
- The best 8 third-place teams also qualify.
- A deterministic Round of 32 bracket is built from the 32 qualifiers.
- Knockouts continue through Round of 16, quarter-finals, semi-finals and final.

Each group match samples goals from the expected-goals model. Knockout draws are resolved with a penalty-style decisive probability derived from the match prediction model. This is documented as a transparent MVP approximation, not an exact recreation of FIFA bracket policy.

## Player Scorer Weighting

Scorer estimates use:

- expected minutes
- goals per 90
- shots per 90
- xG per 90
- penalty taker flag
- set-piece target flag
- team expected goals
- player starting probability
- recent form signal

Player profiles are curated demo seed data for engineering purposes. The data layer is designed so these profiles can be replaced by official FIFA squad lists or football API provider data.

## Golden Boot Logic

The single-run tournament simulator assigns goals in every simulated match from team expected goals. Player goal shares are weighted by:

- goals per 90, shots per 90 and xG per 90;
- expected minutes and starting probability;
- penalty-taker status;
- attacking position;
- aerial/set-piece target profile for defenders and set-piece situations.

The Golden Boot is awarded to the player with the most simulated goals. Ties are resolved by:

1. assists;
2. fewer minutes;
3. team stage reached.

## Tournament MVP Logic

The MVP is not automatically the Golden Boot winner. Each player's award score combines:

- goals weighted at 1.6 points;
- assists weighted at 1.0 point;
- knockout goals weighted at 1.2 points;
- team progression bonus;
- semi-final and final performance bonus;
- a small defensive/team-progression bonus for defenders and goalkeepers.

This is intentionally transparent and inspectable. It gives attacking output real value while allowing a deep-tournament defender or goalkeeper to compete when their team progresses and their performance profile supports it.

## Goal-Type Model

Open-play, set-piece, penalty and counterattack estimates use team threat scores, opponent weaknesses and conservative reference weights.

## Limitations

The demo seed data is illustrative and is labelled as a demo tournament dataset for engineering purposes, not official FIFA fixture data. It does not include live injuries, tactical lineup changes, travel disruption, private training data, referee assignments, betting-market calibration or full historical calibration. Future versions should add model calibration, backtesting, richer event parsing, confidence intervals, exact official bracket mapping and richer defensive/goalkeeper award modelling.
