import Link from "next/link";
import { ArrowRight, FileText, ShieldCheck, Trophy } from "lucide-react";
import { WinnerChart } from "@/components/Charts";
import { MetricCard } from "@/components/MetricCard";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { api } from "@/lib/api";

export default async function HomePage() {
  const [teams, matches, tournament] = await Promise.all([api.teams(), api.matches(), api.tournament()]);
  const upcoming = matches.filter((match) => match.status === "scheduled").slice(0, 4);
  const completed = matches.filter((match) => match.status === "completed");
  const topWinners = tournament.teams.slice(0, 5);

  return (
    <div className="space-y-6">
      <section className="rounded border border-line bg-panel p-6">
        <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-mint">Full-stack football analytics platform</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold text-white">The Scout&apos;s Edge</h1>
            <p className="mt-4 max-w-3xl text-slate-300">
              An automated football analytics pipeline that ingests match and event data, computes tactical and predictive metrics, and presents scouting-style insights through a full-stack dashboard.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            <div className="flex items-center gap-3 rounded border border-line bg-ink p-3">
              <ShieldCheck className="text-mint" size={20} />
              <span className="text-sm text-slate-300">No betting odds or advice</span>
            </div>
            <div className="flex items-center gap-3 rounded border border-line bg-ink p-3">
              <Trophy className="text-amber" size={20} />
              <span className="text-sm text-slate-300">Monte Carlo simulation</span>
            </div>
            <div className="flex items-center gap-3 rounded border border-line bg-ink p-3">
              <FileText className="text-coral" size={20} />
              <span className="text-sm text-slate-300">Rule-based report output</span>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <MetricCard label="Teams" value={String(teams.length)} detail="48-team offline demo dataset" />
        <MetricCard label="Matches" value={String(matches.length)} detail={`${completed.length} completed with event data`} />
        <MetricCard label="Simulation" value={String(tournament.simulation_runs)} detail="Transparent tournament runs" />
        <MetricCard label="Forecasting" value="Model" detail="Poisson-style reference model" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded border border-line bg-panel p-4">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Upcoming Matches</h2>
            <Link href="/matches" className="flex items-center gap-2 text-sm text-mint">
              View all <ArrowRight size={14} />
            </Link>
          </div>
          <div className="space-y-3">
            {upcoming.map((match) => (
              <Link key={match.id} href={`/matches/${match.id}`} className="block rounded border border-line bg-ink p-4 hover:border-mint">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-medium text-white">{match.home_team.name} vs {match.away_team.name}</p>
                    <p className="text-sm text-slate-400">{match.stage} · {match.venue}</p>
                  </div>
                  <span className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-300">{match.status}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white">Top Predicted Winners</h2>
          <WinnerChart teams={topWinners} />
          <div className="grid gap-3">
            {topWinners.slice(0, 3).map((team, index) => (
              <ProbabilityBar key={team.team} label={`${index + 1}. ${team.team}`} value={team.winner_probability} tone={index === 0 ? "mint" : "amber"} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
