import type { GoalTypePrediction, Match, MatchPrediction, PlayerProfile, ScorerCandidate, ShotMapResponse, SingleTournamentRun, Team, TournamentSimulation } from "@/types/api";

const DEFAULT_CLIENT_API_BASE_URL = "http://localhost:8000";

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public readonly url: string,
    public readonly method: string,
    public readonly status?: number,
    public readonly backendMessage?: string
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

export function getClientApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_CLIENT_API_BASE_URL;
}

export function getServerApiBaseUrl(): string {
  return process.env.BACKEND_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_CLIENT_API_BASE_URL;
}

function getApiBaseUrl(): string {
  return typeof window === "undefined" ? getServerApiBaseUrl() : getClientApiBaseUrl();
}

async function readBackendMessage(response: Response): Promise<string | undefined> {
  const contentType = response.headers.get("content-type") ?? "";
  try {
    if (contentType.includes("application/json")) {
      const payload = (await response.json()) as { detail?: unknown; message?: unknown; error?: unknown };
      const detail = payload.detail ?? payload.message ?? payload.error;
      return typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : undefined;
    }
    const text = await response.text();
    return text || undefined;
  } catch {
    return undefined;
  }
}

async function getJson<T>(path: string, init?: RequestInit & { useClientBase?: boolean }): Promise<T> {
  const { useClientBase, ...fetchInit } = init ?? {};
  const baseUrl = useClientBase ? getClientApiBaseUrl() : getApiBaseUrl();
  const url = `${baseUrl}${path}`;
  const method = fetchInit.method ?? "GET";
  let response: Response;
  try {
    response = await fetch(url, { ...fetchInit, cache: "no-store" });
  } catch (error) {
    if (error instanceof Error && error.message.includes("Dynamic server usage")) {
      throw error;
    }
    throw new ApiRequestError(
      `Simulation request failed: ${method} ${url} could not reach the backend${error instanceof Error ? `: ${error.message}` : ""}`,
      url,
      method
    );
  }
  if (!response.ok) {
    const backendMessage = await readBackendMessage(response);
    throw new ApiRequestError(
      `Simulation request failed: ${method} ${url} returned ${response.status}${backendMessage ? `: ${backendMessage}` : ""}`,
      url,
      method,
      response.status,
      backendMessage
    );
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
      useClientBase: true,
    }),
  tournamentGroups: () => getJson<{ groups: Record<string, Team[]> }>("/tournament/groups"),
  tournamentFixtures: () => getJson<{ fixtures: Record<string, unknown>[]; fixture_count: number }>("/tournament/fixtures"),
  scorers: (id: number) => getJson<{ candidates: ScorerCandidate[] }>(`/predictions/scorers/${id}`),
  goalTypes: (id: number) => getJson<{ teams: GoalTypePrediction[] }>(`/predictions/goal-types/${id}`),
};
