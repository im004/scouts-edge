import { ShotMap } from "@/components/Charts";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { api } from "@/lib/api";

export default async function MatchDetailPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const [match, prediction, scorers, goalTypes, analytics, shotMap, chains] = await Promise.all([
    api.match(id),
    api.matchPrediction(id),
    api.scorers(id),
    api.goalTypes(id),
    api.matchAnalytics(id),
    api.shotMap(id),
    api.possessionChains(id)
  ]);

  const isPreMatch = analytics.mode === "pre_match" || !match.has_event_data;
  const teamMetrics = (analytics.teams ?? {}) as Record<string, Record<string, number>>;
  const homeMetrics = teamMetrics?.[match.home_team_id] ?? {};
  const awayMetrics = teamMetrics?.[match.away_team_id] ?? {};
  const preview = analytics.pre_match_preview as { headline: string; summary: string; bullets: string[] } | undefined;
  const completedSummary = analytics.tactical_summary as { headline: string; summary: string; bullets: string[] } | undefined;

  return (
    <div className="space-y-6">
      <section className="rounded border border-line bg-panel p-5">
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
          <div>
            <p className="text-sm uppercase tracking-wide text-mint">{match.stage} · {match.group}</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">{match.home_team.name} vs {match.away_team.name}</h1>
            <p className="mt-2 text-slate-400">{match.venue} · {new Date(match.match_date).toLocaleString()}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="rounded border border-line bg-ink px-2 py-1 text-xs text-slate-300">{match.status}</span>
            <span className={match.has_event_data ? "rounded bg-mint px-2 py-1 text-xs text-ink" : "rounded border border-line bg-ink px-2 py-1 text-xs text-slate-300"}>
              {match.has_event_data ? "Event data available" : "No event data"}
            </span>
          </div>
        </div>
        {match.status === "simulated" ? (
          <p className="mt-3 rounded border border-amber/40 bg-amber/10 p-3 text-sm text-amber">Simulated result — not real match data.</p>
        ) : null}
      </section>

      <section className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-4 text-lg font-semibold text-white">Result Prediction</h2>
          <div className="space-y-4">
            <ProbabilityBar label={`${prediction.team_a} win`} value={prediction.team_a_win_probability} />
            <ProbabilityBar label="Draw" value={prediction.draw_probability} tone="amber" />
            <ProbabilityBar label={`${prediction.team_b} win`} value={prediction.team_b_win_probability} tone="coral" />
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded bg-ink p-3">
              <p className="text-xs text-slate-500">Expected goals</p>
              <p className="text-xl font-semibold text-white">{prediction.team_a_expected_goals} - {prediction.team_b_expected_goals}</p>
            </div>
            <div className="rounded bg-ink p-3">
              <p className="text-xs text-slate-500">Confidence</p>
              <p className="text-xl font-semibold text-white">{prediction.confidence}</p>
            </div>
            <div className="rounded bg-ink p-3">
              <p className="text-xs text-slate-500">Top scoreline</p>
              <p className="text-xl font-semibold text-white">{prediction.most_likely_scorelines[0]?.score}</p>
            </div>
          </div>
        </div>

        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-4 text-lg font-semibold text-white">Shot Map</h2>
          {shotMap.has_shots ? (
            <ShotMap shots={shotMap.shots} />
          ) : (
            <div className="rounded border border-dashed border-line bg-ink p-6">
              <p className="text-lg font-semibold text-white">{shotMap.empty_state?.title}</p>
              <p className="mt-3 text-sm leading-6 text-slate-300">{shotMap.empty_state?.explanation}</p>
              <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
                <div>
                  <dt className="text-slate-500">Match status</dt>
                  <dd className="text-white">{shotMap.empty_state?.match_status}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">Required data</dt>
                  <dd className="text-white">{shotMap.empty_state?.required_data}</dd>
                </div>
              </dl>
              <p className="mt-4 text-sm text-mint">{shotMap.empty_state?.next_action}</p>
            </div>
          )}
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-3 text-lg font-semibold text-white">Tactical Summary</h2>
          {isPreMatch && preview ? (
            <div className="space-y-3 text-sm leading-6 text-slate-300">
              <p className="font-medium text-white">{preview.headline}</p>
              <p>{preview.summary}</p>
              <ul className="space-y-2">
                {preview.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}
              </ul>
            </div>
          ) : (
            <div className="space-y-3 text-sm leading-6 text-slate-300">
              <p className="font-medium text-white">{completedSummary?.headline ?? "Completed match tactical summary"}</p>
              <p>{completedSummary?.summary}</p>
              <p>{match.home_team.name}: {homeMetrics.total_shots ?? 0} shots, {homeMetrics.xg ?? 0} xG, {homeMetrics.dangerous_actions ?? 0} dangerous actions.</p>
              <p>{match.away_team.name}: {awayMetrics.total_shots ?? 0} shots, {awayMetrics.xg ?? 0} xG, {awayMetrics.dangerous_actions ?? 0} dangerous actions.</p>
              <p>{chains.length} possession chains detected from available event data.</p>
            </div>
          )}
        </div>

        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-3 text-lg font-semibold text-white">Scorer Candidates</h2>
          <div className="space-y-3">
            {scorers.candidates.slice(0, 5).map((candidate) => (
              <div key={`${candidate.player_name}`} className="rounded bg-ink p-3">
                <div className="mb-2 flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium text-white">{candidate.player_name}</p>
                    <p className="text-xs text-slate-400">{candidate.team_name} · {candidate.position} · {candidate.role}</p>
                  </div>
                  <span className="text-sm font-semibold text-mint">{Math.round(candidate.probability * 100)}%</span>
                </div>
                <ProbabilityBar label="Scoring probability" value={candidate.probability} />
                <p className="mt-2 text-xs text-slate-500">{candidate.top_factor}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-3 text-lg font-semibold text-white">Goal-Type Probabilities</h2>
          <div className="space-y-4">
            {goalTypes.teams.map((team) => (
              <div key={`${team.team}`} className="rounded bg-ink p-3">
                <p className="mb-2 font-medium text-white">{team.team}</p>
                <div className="space-y-2">
                  <ProbabilityBar label="Open play" value={team.open_play_goal_probability} />
                  <ProbabilityBar label="Set piece" value={team.set_piece_goal_probability} tone="amber" />
                  <ProbabilityBar label="Counter" value={team.counterattack_goal_probability} tone="coral" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
