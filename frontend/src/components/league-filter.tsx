"use client";

import { LEAGUES } from "@/types";
import clsx from "clsx";

interface LeagueFilterProps {
  selected: number | undefined;
  onChange: (leagueId: number | undefined) => void;
}

export function LeagueFilter({ selected, onChange }: LeagueFilterProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onChange(undefined)}
        className={clsx(
          "px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 border",
          selected === undefined
            ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
            : "bg-slate-800/50 border-slate-700/50 text-slate-400 hover:border-slate-600 hover:text-slate-300"
        )}
      >
        All Leagues
      </button>
      {LEAGUES.map((league) => (
        <button
          key={league.id}
          onClick={() => onChange(league.id)}
          className={clsx(
            "px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 border",
            selected === league.id
              ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
              : "bg-slate-800/50 border-slate-700/50 text-slate-400 hover:border-slate-600 hover:text-slate-300"
          )}
        >
          {league.flag} {league.name}
        </button>
      ))}
    </div>
  );
}
