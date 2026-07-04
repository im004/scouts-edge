# Tournament Simulation

The Scout's Edge includes a 48-team offline tournament mode so the project can be demoed without paid APIs.

The dataset is labelled clearly as:

> Demo tournament dataset for engineering purposes, not official FIFA fixture data.

## Format

- 48 teams.
- 12 groups named Group A through Group L.
- 4 teams per group.
- 6 group-stage fixtures per group.
- 72 group-stage fixtures total.
- Top 2 from each group qualify automatically.
- Best 8 third-place teams qualify.
- 32 teams enter the knockout bracket.

## Group-Stage Simulation

For each group-stage match:

- expected goals are calculated for both teams;
- goals are sampled with a Poisson-style model;
- points, wins, draws, losses, goals for, goals against and goal difference are updated.

Group tables are sorted by:

1. points;
2. goal difference;
3. goals scored;
4. seeded team rating as a deterministic fallback;
5. team id as the final deterministic fallback.

The current MVP does not implement official head-to-head rules. That is intentionally documented as a future improvement.

## Third-Place Qualification

After all groups are simulated:

- the top two teams from each group advance automatically;
- the 12 third-place teams are ranked with the same table sorting logic;
- the best 8 third-place teams advance;
- the remaining 16 teams are eliminated.

## Knockout Bracket

The Round of 32 bracket is deterministic but not an exact FIFA bracket mapping. The MVP sorts qualifiers by group rank and table strength, then pairs higher seeds against lower seeds.

Knockout stages:

- Round of 32;
- Round of 16;
- quarter-finals;
- semi-finals;
- final.

If a knockout match is drawn after normal-time simulation, it is resolved with a penalty-style decisive probability derived from the match prediction model.

## Monte Carlo Output

The simulator runs 100 to 10,000 tournament runs. The default is 1,000.

For every team it outputs:

- group-stage probability;
- Round of 32 probability;
- Round of 16 probability;
- quarter-final probability;
- semi-final probability;
- final probability;
- winner probability;
- average points;
- average goals for;
- average goals against.

No team is given a forced 100% quarter-final probability in full-tournament mode.

## Single-Run Simulation

Monte Carlo forecasting answers: "How often does each team reach each stage across many runs?"

The single-run simulator answers a different product question: "What could one complete tournament path look like?" The `POST /tournament/simulate/run` endpoint returns exactly one simulated tournament with:

- one winner and runner-up;
- final score and normal-time or penalties decision state;
- semi-finalists;
- simulated group tables and third-place ranking;
- full knockout path from Round of 32 to final;
- top scorers, Golden Boot and tournament MVP.

An optional seed makes the run deterministic for demos, tests and screenshots. The same seed returns the same winner, final and player-award ordering. Without a seed, the API generates a new one and returns it with the response.

The UI labels this output as one simulated tournament path, not a prediction certainty. This keeps the Monte Carlo probability forecast separate from the interactive "run the tournament once" experience.

## Limitations

- The team list is realistic but not official qualification data.
- The bracket mapping is credible and deterministic, not official.
- The model is a transparent reference model rather than a calibrated forecasting system.
- The simulation does not yet include injuries, suspensions, travel, lineup uncertainty or official tie-break edge cases.

## Future Improvements

- Add exact official bracket mapping once final FIFA rules and fixtures are known.
- Persist tournament simulation runs in PostgreSQL.
- Add backtesting against historical tournaments.
- Add calibration plots and confidence intervals.
- Add live provider ingestion for fixtures, lineups and player availability.
