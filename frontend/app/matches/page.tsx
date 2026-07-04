import Link from "next/link";
import { CalendarDays, Search } from "lucide-react";
import { api } from "@/lib/api";

const badgeClass = "rounded border border-line bg-ink px-2 py-1 text-xs text-slate-300";

export default async function MatchesPage({ searchParams }: { searchParams?: Record<string, string | undefined> }) {
  const matches = await api.matches({
    team: searchParams?.team,
    group: searchParams?.group,
    stage: searchParams?.stage,
    status: searchParams?.status
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-semibold text-white">Matches</h1>
          <p className="mt-2 text-slate-400">Offline demo fixtures with event-data and prediction status.</p>
        </div>
      </div>

      <form className="grid gap-3 rounded border border-line bg-panel p-4 md:grid-cols-5">
        <label className="text-sm text-slate-400">
          Team
          <input name="team" defaultValue={searchParams?.team ?? ""} className="mt-1 w-full rounded border border-line bg-ink px-3 py-2 text-white" />
        </label>
        <label className="text-sm text-slate-400">
          Group
          <select name="group" defaultValue={searchParams?.group ?? ""} className="mt-1 w-full rounded border border-line bg-ink px-3 py-2 text-white">
            <option value="">All</option>
            {"ABCDEFGHIJKL".split("").map((letter) => <option key={letter} value={`Group ${letter}`}>Group {letter}</option>)}
          </select>
        </label>
        <label className="text-sm text-slate-400">
          Stage
          <select name="stage" defaultValue={searchParams?.stage ?? ""} className="mt-1 w-full rounded border border-line bg-ink px-3 py-2 text-white">
            <option value="">All</option>
            <option value="Group Stage">Group Stage</option>
          </select>
        </label>
        <label className="text-sm text-slate-400">
          Status
          <select name="status" defaultValue={searchParams?.status ?? ""} className="mt-1 w-full rounded border border-line bg-ink px-3 py-2 text-white">
            <option value="">All</option>
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="simulated">Simulated</option>
          </select>
        </label>
        <button className="mt-6 flex items-center justify-center gap-2 rounded bg-mint px-3 py-2 text-sm font-semibold text-ink">
          <Search size={15} /> Filter
        </button>
      </form>

      <div className="overflow-hidden rounded border border-line bg-panel">
        <table className="w-full min-w-[980px] text-left text-sm">
          <thead className="border-b border-line bg-ink text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-4 py-3">Match</th>
              <th className="px-4 py-3">Group</th>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Data</th>
              <th className="px-4 py-3">Prediction</th>
            </tr>
          </thead>
          <tbody>
            {matches.map((match) => (
              <tr key={match.id} className="border-b border-line/70 last:border-b-0">
                <td className="px-4 py-3">
                  <Link href={`/matches/${match.id}`} className="font-medium text-white hover:text-mint">
                    {match.home_team.name} vs {match.away_team.name}
                  </Link>
                  <p className="text-xs text-slate-500">{match.venue}</p>
                </td>
                <td className="px-4 py-3 text-slate-300">{match.group}</td>
                <td className="px-4 py-3 text-slate-300">
                  <span className="flex items-center gap-2"><CalendarDays size={14} /> {new Date(match.match_date).toLocaleDateString()}</span>
                </td>
                <td className="px-4 py-3">
                  <span className={badgeClass}>{match.status === "completed" ? "Completed" : match.status === "simulated" ? "Simulated" : "Scheduled"}</span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-2">
                    <span className={match.has_event_data ? "rounded bg-mint px-2 py-1 text-xs text-ink" : badgeClass}>
                      {match.has_event_data ? "Event data available" : "No event data"}
                    </span>
                    {match.status === "simulated" ? <span className={badgeClass}>Simulated result</span> : null}
                  </div>
                </td>
                <td className="px-4 py-3 text-amber">Prediction available</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
