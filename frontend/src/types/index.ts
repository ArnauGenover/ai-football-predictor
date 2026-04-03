export interface TeamBrief {
  id: number;
  name: string;
  logo_url: string | null;
}

export interface Prediction {
  fixture_id: number;
  prob_home_win: number;
  prob_draw: number;
  prob_away_win: number;
  predicted_winner_id: number | null;
  model_version: string | null;
  created_at: string;
  fixture_date: string | null;
  league_id: number | null;
  status: string | null;
  home_team: TeamBrief | null;
  away_team: TeamBrief | null;
}

export interface League {
  id: number;
  name: string;
  flag: string;
}

export const LEAGUES: League[] = [
  { id: 39, name: "Premier League", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿" },
  { id: 140, name: "La Liga", flag: "🇪🇸" },
  { id: 135, name: "Serie A", flag: "🇮🇹" },
  { id: 78, name: "Bundesliga", flag: "🇩🇪" },
  { id: 61, name: "Ligue 1", flag: "🇫🇷" },
];
