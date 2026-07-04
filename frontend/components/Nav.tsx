import Link from "next/link";
import { Activity, BarChart3, Info, Shield, Trophy } from "lucide-react";

const links = [
  { href: "/", label: "Dashboard", icon: Activity },
  { href: "/matches", label: "Matches", icon: Shield },
  { href: "/tournament", label: "Tournament", icon: Trophy },
  { href: "/teams/1", label: "Teams", icon: BarChart3 },
  { href: "/methodology", label: "Method", icon: Info }
];

export function Nav() {
  return (
    <nav className="sticky top-0 z-20 border-b border-line bg-ink/92 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded bg-mint text-ink">
            <BarChart3 size={19} />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-mint">The Scout&apos;s Edge</p>
            <p className="text-xs text-slate-400">Football analytics pipeline</p>
          </div>
        </Link>
        <div className="flex flex-wrap items-center justify-end gap-2">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <Link key={link.href} href={link.href} className="flex items-center gap-2 rounded border border-line px-3 py-2 text-sm text-slate-200 hover:border-mint hover:text-white">
                <Icon size={15} />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
