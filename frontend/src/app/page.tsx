"use client";

import { useState } from "react";
import { TrendingUp, Loader2, Radar } from "lucide-react";
import { usePredictions } from "@/lib/hooks";
import { MatchCard } from "@/components/match-card";
import { LeagueFilter } from "@/components/league-filter";

export default function Home() {
  const [leagueId, setLeagueId] = useState<number | undefined>(undefined);
  const { data: predictions, isLoading, error } = usePredictions(leagueId);

  const count = predictions?.length ?? 0;

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="rounded-2xl bg-gradient-to-br from-slate-800/50 via-slate-900/50 to-emerald-900/20 border border-slate-800/50 p-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-100">
              Match Predictions
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              AI-generated probabilities for upcoming fixtures across Europe's
              top 5 leagues
            </p>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-slate-800/80 border border-slate-700/50 px-5 py-3">
            <TrendingUp className="h-5 w-5 text-emerald-400" />
            <div>
              <p className="text-2xl font-bold text-slate-100">{count}</p>
              <p className="text-[11px] text-slate-500 font-medium -mt-0.5">
                Live Predictions
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* League filter */}
      <LeagueFilter selected={leagueId} onChange={setLeagueId} />

      {/* Grid */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <Loader2 className="h-8 w-8 text-emerald-400 animate-spin" />
          <p className="text-sm text-slate-500">Loading predictions...</p>
        </div>
      )}

      {error && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-8 text-center">
          <p className="text-sm text-red-400">
            Failed to load predictions. Is the backend running on port 7860?
          </p>
        </div>
      )}

      {!isLoading && !error && count === 0 && (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-800/50 border border-slate-700/50">
            <Radar className="h-8 w-8 text-slate-600" />
          </div>
          <div className="text-center">
            <p className="text-lg font-semibold text-slate-300">
              Scanning for upcoming matches...
            </p>
            <p className="mt-1 text-sm text-slate-500">
              No predictions available yet. Run the collector and ML pipeline to
              generate forecasts.
            </p>
          </div>
        </div>
      )}

      {!isLoading && !error && count > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {predictions!.map((p) => (
            <MatchCard key={p.fixture_id} prediction={p} />
          ))}
        </div>
      )}
    </div>
  );
}
