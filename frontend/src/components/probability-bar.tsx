"use client";

import { pct } from "@/lib/format";

interface ProbabilityBarProps {
  home: number;
  draw: number;
  away: number;
}

export function ProbabilityBar({ home, draw, away }: ProbabilityBarProps) {
  const hPct = home * 100;
  const dPct = draw * 100;
  const aPct = away * 100;

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs font-medium">
        <span className="text-emerald-400">Home {pct(home)}</span>
        <span className="text-slate-400">Draw {pct(draw)}</span>
        <span className="text-blue-400">Away {pct(away)}</span>
      </div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="bg-emerald-500 transition-all duration-500"
          style={{ width: `${hPct}%` }}
        />
        <div
          className="bg-slate-500 transition-all duration-500"
          style={{ width: `${dPct}%` }}
        />
        <div
          className="bg-blue-500 transition-all duration-500"
          style={{ width: `${aPct}%` }}
        />
      </div>
    </div>
  );
}
