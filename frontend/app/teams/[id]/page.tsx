import Link from "next/link";
import { ProbabilityBar } from "@/components/ProbabilityBar";
import { api } from "@/lib/api";

export default async function TeamPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const [team, analytics, teams] = await Promise.all([api.team(id), api.teamAnalytics(id), api.teams()]);
  const rating = team.rating ?? {};
  const metrics = analytics.recent_match_metrics as Record<string, number>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-semibold text-white">{team.name}</h1>
          <p className="mt-2 text-slate-400">Team profile with ratings, player features and recent event metrics.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {teams.map((item) => (
            <Link key={item.id} href={`/teams/${item.id}`} className="rounded border border-line px-3 py-2 text-sm text-slate-300 hover:border-mint">
              {item.short_name}
            </Link>
          ))}
        </div>
      </div>

      <section className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-4 text-lg font-semibold text-white">Rating Profile</h2>
          <div className="space-y-4">
            <ProbabilityBar label="Attack" value={Number(rating.attack_strength ?? 0)} />
            <ProbabilityBar label="Defence" value={Number(rating.defence_strength ?? 0)} tone="amber" />
            <ProbabilityBar label="Recent form" value={Number(rating.recent_form ?? 0)} />
            <ProbabilityBar label="Set-piece threat" value={Number(rating.set_piece_threat ?? 0)} tone="coral" />
            <ProbabilityBar label="Open-play threat" value={Number(rating.open_play_threat ?? 0)} />
          </div>
        </div>

        <div className="rounded border border-line bg-panel p-4">
          <h2 className="mb-4 text-lg font-semibold text-white">Player Involvement Inputs</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {team.players.map((player) => (
              <div key={player.id} className="rounded border border-line bg-ink p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium text-white">{player.player_name ?? player.name}</p>
                    <p className="text-sm text-slate-400">{player.position} · {player.role}</p>
                  </div>
                  <span className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-300">{Math.round(player.features.expected_minutes)} mins</span>
                </div>
                <p className="mt-2 text-xs text-slate-500">
                  xG/90 {player.features.xg_per_90} · shots/90 {player.features.shots_per_90} · goals/90 {player.features.goals_per_90}
                  {player.features.creative_threat ? " · creative threat" : ""}
                  {player.features.aerial_threat ? " · aerial threat" : ""}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded border border-line bg-panel p-4">
          <p className="text-xs text-slate-500">Events</p>
          <p className="text-2xl font-semibold text-white">{metrics.events ?? 0}</p>
        </div>
        <div className="rounded border border-line bg-panel p-4">
          <p className="text-xs text-slate-500">Shots</p>
          <p className="text-2xl font-semibold text-white">{metrics.shots ?? 0}</p>
        </div>
        <div className="rounded border border-line bg-panel p-4">
          <p className="text-xs text-slate-500">xG</p>
          <p className="text-2xl font-semibold text-white">{metrics.xg ?? 0}</p>
        </div>
        <div className="rounded border border-line bg-panel p-4">
          <p className="text-xs text-slate-500">Set-piece shots</p>
          <p className="text-2xl font-semibold text-white">{metrics.set_piece_shots ?? 0}</p>
        </div>
      </section>
    </div>
  );
}
