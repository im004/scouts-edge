"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TournamentTeam } from "@/types/api";

export function WinnerChart({ teams }: { teams: TournamentTeam[] }) {
  return (
    <div className="h-80 rounded border border-line bg-panel p-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={teams}>
          <CartesianGrid stroke="#263841" vertical={false} />
          <XAxis dataKey="team" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <YAxis stroke="#94a3b8" tickFormatter={(value) => `${Math.round(Number(value) * 100)}%`} />
          <Tooltip
            cursor={{ fill: "rgba(72,213,151,0.08)" }}
            contentStyle={{ background: "#111c22", border: "1px solid #263841", color: "#fff" }}
            formatter={(value) => `${Math.round(Number(value) * 100)}%`}
          />
          <Bar dataKey="winner_probability" fill="#48d597" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ShotMap({ shots }: { shots: Record<string, unknown>[] }) {
  if (!shots.length) {
    return null;
  }

  return (
    <div className="relative aspect-[12/8] overflow-hidden rounded border border-line bg-pitch pitch-grid">
      <div className="absolute left-1/2 top-0 h-full w-px bg-white/20" />
      <div className="absolute left-0 top-[18%] h-[64%] w-[18%] border border-white/20" />
      <div className="absolute right-0 top-[18%] h-[64%] w-[18%] border border-white/20" />
      {shots.map((shot, index) => {
        const x = Number(shot.x ?? 0) / 120 * 100;
        const y = Number(shot.y ?? 0) / 80 * 100;
        const isGoal = shot.shot_outcome === "Goal";
        return (
          <div
            key={`${shot.player}-${index}`}
            title={`${shot.player} ${shot.shot_outcome}`}
            className={`absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white ${isGoal ? "bg-coral" : "bg-mint"}`}
            style={{ left: `${x}%`, top: `${y}%` }}
          />
        );
      })}
    </div>
  );
}
