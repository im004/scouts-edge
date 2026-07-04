type ProbabilityBarProps = {
  label: string;
  value: number;
  tone?: "mint" | "amber" | "coral";
};

const colors = {
  mint: "bg-mint",
  amber: "bg-amber",
  coral: "bg-coral"
};

export function ProbabilityBar({ label, value, tone = "mint" }: ProbabilityBarProps) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="font-medium text-white">{Math.round(value * 100)}%</span>
      </div>
      <div className="h-2 rounded bg-slate-800">
        <div className={`h-2 rounded ${colors[tone]}`} style={{ width: `${Math.max(4, value * 100)}%` }} />
      </div>
    </div>
  );
}
