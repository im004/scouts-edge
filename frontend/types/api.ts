export type Team = {
  id: number;
  name: string;
  short_name: string;
  country?: string;
  country_code?: string;
  group?: string;
  fifa_rank?: number;
  rating?: Record<string, number>;
};

export type Match = {
  id: number;
  home_team_id: number;
  away_team_id: number;
  match_date: string;
  stage: string;
  group?: string;
  venue?: string;
  status: string;
  home_score?: number;
  away_score?: number;
  home_team: Team;
  away_team: Team;
  has_event_data: boolean;
  event_count: number;
};

export type MatchPrediction = {
  match_id: number;
  team_a: string;
  team_b: string;
  team_a_win_probability: number;
  draw_probability: number;
  team_b_win_probability: number;
  team_a_expected_goals: number;
  team_b_expected_goals: number;
  most_likely_scorelines: { score: string; probability: number }[];
  confidence: "Low" | "Medium" | "High";
  explanation: string[];
};

export type TournamentTeam = {
  team_id: number;
  team: string;
  group: string;
  group_stage_probability: number;
  round_of_32_probability: number;
  round_of_16_probability: number;
  quarter_final_probability: number;
  semi_final_probability: number;
  final_probability: number;
  winner_probability: number;
  average_points: number;
  average_goals_for: number;
  average_goals_against: number;
};

export type ScorerCandidate = {
  player_name: string;
  team_name: string;
  team_code: string;
  position: string;
  role: string;
  probability: number;
  top_factor: string;
  features: {
    expected_minutes: number;
    goals_per_90: number;
    shots_per_90: number;
    xg_per_90: number;
    penalty_taker: boolean;
    set_piece_taker: boolean;
    aerial_threat: boolean;
    creative_threat: boolean;
  };
  player: string;
  team: string;
  anytime_scorer_probability: number;
  first_scorer_probability: number;
  confidence: "Low" | "Medium" | "High";
  explanation: string[];
};

export type PlayerProfile = {
  id: number;
  team_id: number;
  name: string;
  player_name: string;
  team_name: string;
  team_code: string;
  position: string;
  role: string;
  features: ScorerCandidate["features"] & {
    starting_probability: number;
    mvp_rating_base: number;
  };
  profile_source: string;
};

export type GoalTypePrediction = {
  match_id: number;
  team: string;
  open_play_goal_probability: number;
  set_piece_goal_probability: number;
  penalty_goal_probability: number;
  counterattack_goal_probability: number;
  confidence: "Low" | "Medium";
  explanation: string[];
};

export type GroupTableRow = {
  team_id: number;
  team: string;
  group: string;
  rank: number;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  points: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  base_rating: number;
};

export type TournamentSimulation = {
  mode: string;
  simulation_runs: number;
  format: string;
  winner: string;
  teams: TournamentTeam[];
  group_tables: Record<string, GroupTableRow[]>;
  third_place_ranking: GroupTableRow[];
  selected_third_place_qualifiers: GroupTableRow[];
  eliminated_teams: GroupTableRow[];
  bracket: Record<string, KnockoutMatch[]>;
};

export type SingleTournamentRun = {
  simulation_id: string;
  seed: number;
  winner: Team;
  runner_up: Team;
  final: {
    team_a: string;
    team_b: string;
    score: string;
    decided_by: "normal_time" | "penalties";
  };
  semi_finalists: Team[];
  group_tables: { group: string; table: GroupTableRow[] }[];
  third_place_table: GroupTableRow[];
  knockout_rounds: {
    round: string;
    matches: {
      team_a: string;
      team_b: string;
      score: string;
      winner: string;
      loser: string;
      decided_by: "normal_time" | "penalties";
    }[];
  }[];
  golden_boot: PlayerAward;
  tournament_mvp: PlayerAward;
  top_scorers: PlayerAward[];
  mvp_leaderboard: PlayerAward[];
  methodology: string;
};

export type PlayerAward = {
  player_name: string;
  team: string;
  team_code: string;
  position: string;
  role: string;
  goals: number;
  assists: number;
  minutes: number;
  knockout_goals: number;
  team_stage_reached: string;
  rating: number;
};

export type KnockoutMatch = {
  stage: string;
  team_a: string;
  team_b: string;
  team_a_goals: number;
  team_b_goals: number;
  winner: string;
  loser: string;
  decided_by: "normal_time" | "penalties";
};

export type ShotMapResponse = {
  has_shots: boolean;
  shots: Record<string, unknown>[];
  empty_state: null | {
    title: string;
    match_status: string;
    has_event_data: boolean;
    explanation: string;
    required_data: string;
    next_action: string;
  };
};
