"use client";

import { useState } from "react";
import { Trophy, Loader2, Play, Medal } from "lucide-react";
import type { SingleTournamentRun } from "@/types/api";
import { ApiRequestError, api } from "@/lib/api";

export function SingleTournamentSimulation() {
  const [seed, setSeed] = useState("");
  const [result, setResult] = useState<SingleTournamentRun | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSimulation() {
    setIsLoading(true);
    setError(null);
    try {
      const parsedSeed = seed.trim() ? Number(seed) : undefined;
      if (parsedSeed !== undefined && Number.isNaN(parsedSeed)) {
        throw new Error("Seed must be a number.");
      }
      setResult(await api.runSingleTournament(parsedSeed));
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.message);
      } else {
        setError(err instanceof Error ? err.message : "Simulation failed.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="space-y-5 rounded border border-line bg-panel p-4">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="text-xs uppercase tracking-wide text-mint">Single Tournament Simulation</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Run one tournament path</h2>
          <p className="mt-2 text-sm text-slate-400">This is one simulated tournament path, not a prediction certainty.</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
          <label className="text-sm text-slate-400">
            Simulation seed
            <input
              value={seed}
              onChange={(event) => setSeed(event.target.value)}
              placeholder="optional"
              className="mt-1 w-full rounded border border-line bg-ink px-3 py-2 text-white"
            />
          </label>
          <button
            onClick={runSimulation}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 rounded bg-mint px-4 py-2 text-sm font-semibold text-ink disabled:opacity-60"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
            Run Tournament Simulation
          </button>
        </div>
      </div>

      {error ? <p className="rounded border border-coral/50 bg-coral/10 p-3 text-sm text-coral">{error}</p> : null}

      {result ? (
        <div className="space-y-5">
          <div className="grid gap-4 md:grid-cols-5">
            <ResultCard label="Winner" value={result.winner.name} detail={`Seed ${result.seed}`} icon="trophy" />
            <ResultCard label="Runner-up" value={result.runner_up.name} detail="Finalist" />
            <ResultCard label="Final score" value={result.final.score} detail={`${result.final.team_a} vs ${result.final.team_b}`} />
            <ResultCard label="Golden Boot" value={result.golden_boot.player_name} detail={`${result.golden_boot.goals} goals · ${result.golden_boot.team}`} icon="medal" />
            <ResultCard label="Tournament MVP" value={result.tournament_mvp.player_name} detail={`${result.tournament_mvp.rating} rating · ${result.tournament_mvp.team}`} icon="medal" />
          </div>

          <div className="rounded border border-line bg-ink p-3 text-sm text-slate-300">
            Semi-finalists: {result.semi_finalists.map((team) => team.name).join(", ")}
          </div>

          <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded border border-line bg-ink p-4">
              <h3 className="mb-3 text-lg font-semibold text-white">Knockout bracket path</h3>
              <div className="grid gap-3 md:grid-cols-2">
                {result.knockout_rounds.map((round) => (
                  <div key={round.round} className="rounded border border-line bg-panel p-3">
                    <p className="mb-2 font-medium text-white">{round.round}</p>
                    <div className="space-y-2 text-xs text-slate-300">
                      {round.matches.map((match, index) => (
                        <p key={`${round.round}-${index}`}>
                          {match.team_a} {match.score} {match.team_b}
                          <span className="text-mint"> · {match.winner}</span>
                          {match.decided_by === "penalties" ? <span className="text-amber"> pens</span> : null}
                        </p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Leaderboard title="Top scorers" players={result.top_scorers.slice(0, 10)} mode="goals" />
          </div>

          <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
            <Leaderboard title="Best player ranking" players={result.mvp_leaderboard.slice(0, 10)} mode="rating" />
            <div className="rounded border border-line bg-ink p-4">
              <h3 className="mb-3 text-lg font-semibold text-white">Group tables from this run</h3>
              <div className="grid gap-3 md:grid-cols-2">
                {result.group_tables.map((group) => (
                  <div key={group.group} className="rounded border border-line bg-panel p-3">
                    <p className="mb-2 font-medium text-white">{group.group}</p>
                    <div className="space-y-1 text-xs text-slate-300">
                      {group.table.map((row) => (
                        <p key={row.team_id}>{row.rank}. {row.team} · {row.points} pts · GD {row.goal_difference}</p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function ResultCard({ label, value, detail, icon }: { label: string; value: string; detail: string; icon?: "trophy" | "medal" }) {
  return (
    <div className="rounded border border-line bg-ink p-4">
      <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-slate-500">
        {icon === "trophy" ? <Trophy size={14} className="text-mint" /> : icon === "medal" ? <Medal size={14} className="text-amber" /> : null}
        {label}
      </div>
      <p className="text-lg font-semibold text-white">{value}</p>
      <p className="mt-1 text-xs text-slate-400">{detail}</p>
    </div>
  );
}

function Leaderboard({ title, players, mode }: { title: string; players: SingleTournamentRun["top_scorers"]; mode: "goals" | "rating" }) {
  return (
    <div className="rounded border border-line bg-ink p-4">
      <h3 className="mb-3 text-lg font-semibold text-white">{title}</h3>
      <div className="space-y-2 text-sm">
        {players.map((player, index) => (
          <div key={`${title}-${player.team_code}-${player.player_name}`} className="grid grid-cols-[1.5rem_1fr_auto] gap-3 rounded bg-panel px-3 py-2">
            <span className="text-slate-500">{index + 1}</span>
            <span>
              <span className="font-medium text-white">{player.player_name}</span>
              <span className="block text-xs text-slate-400">{player.team} · {player.position} · {player.team_stage_reached}</span>
            </span>
            <span className="text-right text-mint">
              {mode === "goals" ? `${player.goals}G ${player.assists}A` : `${player.rating}`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
