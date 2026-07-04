import { WinnerChart } from "@/components/Charts";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { SingleTournamentSimulation } from "@/components/SingleTournamentSimulation";
import { api } from "@/lib/api";

export default async function TournamentPage() {
  const tournament = await api.tournament();
  const topTeams = tournament.teams.slice(0, 12);
  const groupEntries = Object.entries(tournament.group_tables);
  const selectedThirdIds = new Set(tournament.selected_third_place_qualifiers.map((team) => team.team_id));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-white">Tournament Prediction</h1>
        <p className="mt-2 text-slate-400">Full 48-team demo simulation from group stage to final.</p>
      </div>

      <SingleTournamentSimulation />

      <section className="space-y-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-mint">Probability Forecast</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Monte Carlo stage probabilities</h2>
        </div>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded border border-line bg-panel p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Simulation mode</p>
          <p className="mt-2 text-xl font-semibold text-white">Full tournament</p>
          <p className="mt-2 text-sm text-slate-400">Offline demo tournament model</p>
        </div>
        <div className="rounded border border-line bg-panel p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Runs</p>
          <p className="mt-2 text-xl font-semibold text-white">{tournament.simulation_runs}</p>
          <p className="mt-2 text-sm text-slate-400">Group stage, third-place ranking, Round of 32 and knockouts.</p>
        </div>
        <div className="rounded border border-line bg-panel p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Latest sample winner</p>
          <p className="mt-2 text-xl font-semibold text-white">{tournament.winner}</p>
          <p className="mt-2 text-sm text-slate-400">Offline demo simulation, not official FIFA fixture data.</p>
        </div>
      </section>

      <WinnerChart teams={topTeams} />

      <section className="overflow-hidden rounded border border-line bg-panel">
        <div className="border-b border-line p-4">
          <h2 className="text-lg font-semibold text-white">Stage Progression</h2>
        </div>
        <table className="w-full min-w-[980px] text-left text-sm">
          <thead className="border-b border-line bg-ink text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-4 py-3">Team</th>
              <th className="px-4 py-3">Group</th>
              <th className="px-4 py-3">R32</th>
              <th className="px-4 py-3">R16</th>
              <th className="px-4 py-3">QF</th>
              <th className="px-4 py-3">SF</th>
              <th className="px-4 py-3">Final</th>
              <th className="px-4 py-3">Winner</th>
            </tr>
          </thead>
          <tbody>
            {tournament.teams.map((team) => (
              <tr key={team.team_id} className="border-b border-line/70 last:border-b-0">
                <td className="px-4 py-3 font-medium text-white">{team.team}</td>
                <td className="px-4 py-3 text-slate-300">{team.group}</td>
                <td className="px-4 py-3">{Math.round(team.round_of_32_probability * 100)}%</td>
                <td className="px-4 py-3">{Math.round(team.round_of_16_probability * 100)}%</td>
                <td className="px-4 py-3">{Math.round(team.quarter_final_probability * 100)}%</td>
                <td className="px-4 py-3">{Math.round(team.semi_final_probability * 100)}%</td>
                <td className="px-4 py-3">{Math.round(team.final_probability * 100)}%</td>
                <td className="px-4 py-3 min-w-40">
                  <ProbabilityBar label="Winner" value={team.winner_probability} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        {groupEntries.map(([group, rows]) => (
          <div key={group} className="rounded border border-line bg-panel p-4">
            <h2 className="mb-3 text-lg font-semibold text-white">{group}</h2>
            <div className="space-y-2 text-sm">
              {rows.map((row) => (
                <div key={row.team_id} className="grid grid-cols-[1.5rem_1fr_2rem_2rem_2rem] gap-2 rounded bg-ink px-3 py-2 text-slate-300">
                  <span className="text-slate-500">{row.rank}</span>
                  <span className="font-medium text-white">{row.team}</span>
                  <span>{row.points} pts</span>
                  <span>GD {row.goal_difference}</span>
                  <span>{row.goals_for} GF</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>

      <section className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-3 text-lg font-semibold text-white">Best Third-Place Ranking</h2>
          <div className="space-y-2 text-sm">
            {tournament.third_place_ranking.map((row, index) => (
              <div key={row.team_id} className="flex items-center justify-between rounded bg-ink px-3 py-2">
                <span className="text-slate-300">{index + 1}. {row.team} · {row.group}</span>
                <span className={selectedThirdIds.has(row.team_id) ? "text-mint" : "text-slate-500"}>
                  {selectedThirdIds.has(row.team_id) ? "Qualified" : "Eliminated"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-3 text-lg font-semibold text-white">Knockout Bracket Snapshot</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {Object.entries(tournament.bracket).map(([stage, matches]) => (
              <div key={stage} className="rounded bg-ink p-3">
                <p className="mb-2 font-medium text-white">{stage}</p>
                <div className="space-y-2 text-xs text-slate-300">
                  {matches.slice(0, 4).map((match, index) => (
                    <p key={`${stage}-${index}`}>
                      {match.team_a} {match.team_a_goals}-{match.team_b_goals} {match.team_b}
                      <span className="text-mint"> · {match.winner}</span>
                      {match.decided_by === "penalties" ? <span className="text-amber"> pens</span> : null}
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="rounded border border-line bg-panel p-4 text-sm leading-6 text-slate-300">
        Methodology: each run simulates 72 group-stage matches, ranks groups by points, goal difference, goals scored and seeded team rating, advances the top two plus the best eight third-place teams, then plays a deterministic Round of 32 bracket through the final. Drawn knockout matches are resolved with a penalty-style decisive probability.
      </div>
      </section>
    </div>
  );
}
