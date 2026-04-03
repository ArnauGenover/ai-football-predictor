export function formatMatchDate(isoDate: string | null): string {
  if (!isoDate) return "TBD";
  const d = new Date(isoDate);
  return d.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
}

export function formatMatchTime(isoDate: string | null): string {
  if (!isoDate) return "";
  const d = new Date(isoDate);
  return d.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}
