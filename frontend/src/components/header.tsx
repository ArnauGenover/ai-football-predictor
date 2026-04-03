"use client";

import { BrainCircuit, Activity } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <BrainCircuit className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-slate-100">
              AI Football Predictor
            </h1>
            <p className="text-[11px] text-slate-500 font-medium -mt-0.5">
              Machine Learning Match Analysis
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Activity className="h-3.5 w-3.5 text-emerald-500 animate-pulse" />
          <span>Live</span>
        </div>
      </div>
    </header>
  );
}
