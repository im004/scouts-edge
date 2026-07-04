export default function MethodologyPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-white">Methodology</h1>
        <p className="mt-2 max-w-3xl text-slate-400">The system is designed as transparent football analytics, not gambling advice. Every estimate is tied to visible model inputs and explicit limitations.</p>
      </div>

      <section className="grid gap-5 md:grid-cols-2">
        {[
          ["Data Sources", "Offline demo mode uses a labelled 48-team dataset, named player profiles, fixtures and event data shaped like common football event feeds. Provider adapters prepare the codebase for StatsBomb Open Data-style files and future API providers."],
          ["Prediction Model", "Match predictions use attack strength, defence strength, recent form and a Poisson-style scoreline model. Tournament output is produced by Monte Carlo simulation over those match probabilities."],
          ["Scorer Candidates", "Player estimates combine expected minutes, goals per 90, shots per 90, xG per 90, role flags, starting probability and team expected goals."],
          ["Goal Types", "Open-play, set-piece, penalty and counterattack probabilities are estimated separately using team threat profiles and opponent weakness inputs."],
          ["LLM Safety", "The report service is rule-based in the MVP. A future LLM summariser should only receive calculated backend JSON and must not invent injuries, team news or unavailable metrics."],
          ["Limitations", "Demo data is illustrative. The model is a transparent reference model suitable for engineering demonstration and scouting-style exploration, not certainty or betting guidance."]
        ].map(([title, copy]) => (
          <article key={title} className="rounded border border-line bg-panel p-5">
            <h2 className="text-lg font-semibold text-white">{title}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">{copy}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
