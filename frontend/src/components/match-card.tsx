"use client";

import { CalendarDays, Clock, Sparkles } from "lucide-react";
import { formatMatchDate, formatMatchTime, pct } from "@/lib/format";
import { ProbabilityBar } from "@/components/probability-bar";
import { LEAGUES } from "@/types";
import type { Prediction } from "@/types";

interface MatchCardProps {
  prediction: Prediction;
}

function TeamColumn({
  name,
  logoUrl,
  prob,
  isWinner,
  side,
}: {
  name: string;
  logoUrl: string | null;
  prob: number;
  isWinner: boolean;
  side: "home" | "away";
}) {
  return (
    <div className="flex flex-col items-center gap-2 flex-1 min-w-0">
      <div className="relative">
        {logoUrl ? (
          <img
            src={logoUrl}
            alt={name}
            className="h-12 w-12 object-contain drop-shadow-lg"
          />
        ) : (
          <div className="h-12 w-12 rounded-full bg-slate-700 flex items-center justify-center text-lg font-bold text-slate-400">
            {name.charAt(0)}
          </div>
        )}
        {isWinner && (
          <div className="absolute -top-1 -right-1 flex items-center gap-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 px-1.5 py-0.5">
            <Sparkles className="h-2.5 w-2.5 text-emerald-400" />
          </div>
        )}
      </div>
      <span className="text-sm font-semibold text-slate-100 text-center leading-tight truncate w-full">
        {name}
      </span>
      <span
        className={`text-lg font-bold ${
          isWinner ? "text-emerald-400" : "text-slate-400"
        }`}
      >
        {pct(prob)}
      </span>
      {isWinner && (
        <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-2 py-0.5">
          AI Pick
        </span>
      )}
    </div>
  );
}

export function MatchCard({ prediction }: MatchCardProps) {
  const {
    home_team,
    away_team,
    prob_home_win,
    prob_draw,
    prob_away_win,
    fixture_date,
    league_id,
    predicted_winner_id,
  } = prediction;

  const homeName = home_team?.name ?? "Home";
  const awayName = away_team?.name ?? "Away";
  const homeLogo = home_team?.logo_url ?? null;
  const awayLogo = away_team?.logo_url ?? null;

  const homeIsWinner = predicted_winner_id === home_team?.id && prob_draw < prob_home_win;
  const awayIsWinner = predicted_winner_id === away_team?.id && prob_draw < prob_away_win;
  const isDraw = !homeIsWinner && !awayIsWinner;

  const league = LEAGUES.find((l) => l.id === league_id);

  return (
    <div className="group rounded-2xl bg-gradient-to-b from-slate-800/80 to-slate-900/80 border border-slate-700/50 hover:border-emerald-500/30 transition-all duration-300 p-5 backdrop-blur-sm">
      {/* League + Date header */}
      <div className="flex items-center justify-between mb-4 text-xs text-slate-500">
        <span className="flex items-center gap-1.5 font-medium">
          {league ? (
            <>
              <span>{league.flag}</span>
              <span>{league.name}</span>
            </>
          ) : (
            <span>League {league_id}</span>
          )}
        </span>
        <span className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <CalendarDays className="h-3 w-3" />
            {formatMatchDate(fixture_date)}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {formatMatchTime(fixture_date)}
          </span>
        </span>
      </div>

      {/* Teams */}
      <div className="flex items-start justify-between gap-3 mb-5">
        <TeamColumn
          name={homeName}
          logoUrl={homeLogo}
          prob={prob_home_win}
          isWinner={homeIsWinner}
          side="home"
        />

        <div className="flex flex-col items-center justify-center pt-3 shrink-0">
          <span className="text-xs font-bold text-slate-600 uppercase tracking-widest">
            vs
          </span>
          {isDraw && (
            <span className="mt-2 text-[10px] font-semibold uppercase tracking-wider text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-full px-2 py-0.5">
              Draw likely
            </span>
          )}
        </div>

        <TeamColumn
          name={awayName}
          logoUrl={awayLogo}
          prob={prob_away_win}
          isWinner={awayIsWinner}
          side="away"
        />
      </div>

      {/* Probability bar */}
      <ProbabilityBar home={prob_home_win} draw={prob_draw} away={prob_away_win} />

      {/* Model version */}
      <div className="mt-3 flex items-center justify-end">
        <span className="text-[10px] text-slate-600 font-mono">
          {prediction.model_version ?? "rf_v1"}
        </span>
      </div>
    </div>
  );
}
