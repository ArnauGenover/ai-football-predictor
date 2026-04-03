"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import type { Prediction } from "@/types";

export function usePredictions(leagueId?: number) {
  const path = leagueId
    ? `/predictions?league_id=${leagueId}&limit=50`
    : "/predictions?limit=50";

  return useQuery<Prediction[]>({
    queryKey: ["predictions", leagueId],
    queryFn: () => apiFetch<Prediction[]>(path),
  });
}
