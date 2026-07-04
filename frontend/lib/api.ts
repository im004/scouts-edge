import type { GoalTypePrediction, Match, MatchPrediction, PlayerProfile, ScorerCandidate, ShotMapResponse, SingleTournamentRun, Team, TournamentSimulation } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${path}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  teams: () => getJson<Team[]>("/teams"),
  team: (id: number) => getJson<Team & { players: PlayerProfile[] }>(`/teams/${id}`),
  teamAnalytics: (id: number) => getJson<Record<string, unknown>>(`/teams/${id}/analytics`),
  matches: (query?: Record<string, string | undefined>) => {
    const params = new URLSearchParams();
    Object.entries(query ?? {}).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    const suffix = params.toString() ? `?${params.toString()}` : "";
    return getJson<Match[]>(`/matches${suffix}`);
  },
  match: (id: number) => getJson<Match>(`/matches/${id}`),
  matchAnalytics: (id: number) => getJson<Record<string, unknown>>(`/matches/${id}/analytics`),
  shotMap: (id: number) => getJson<ShotMapResponse>(`/matches/${id}/shot-map`),
  possessionChains: (id: number) => getJson<Record<string, unknown>[]>(`/matches/${id}/possession-chains`),
  matchPrediction: (id: number) => getJson<MatchPrediction>(`/predictions/match/${id}`),
  tournament: () => getJson<TournamentSimulation>("/tournament/simulate/latest"),
  runSingleTournament: (seed?: number) =>
    getJson<SingleTournamentRun>("/tournament/simulate/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seed, include_awards: true }),
    }),
  tournamentGroups: () => getJson<{ groups: Record<string, Team[]> }>("/tournament/groups"),
  tournamentFixtures: () => getJson<{ fixtures: Record<string, unknown>[]; fixture_count: number }>("/tournament/fixtures"),
  scorers: (id: number) => getJson<{ candidates: ScorerCandidate[] }>(`/predictions/scorers/${id}`),
  goalTypes: (id: number) => getJson<{ teams: GoalTypePrediction[] }>(`/predictions/goal-types/${id}`),
};
