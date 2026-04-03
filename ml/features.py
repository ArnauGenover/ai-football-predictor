"""
Feature engineering: transforms raw fixture/result data into ML-ready feature vectors.

Features per fixture:
  - home_form / away_form:        points earned in last N matches (W=3, D=1, L=0)
  - home_goals_scored_avg:        avg goals scored by home team in last N
  - home_goals_conceded_avg:      avg goals conceded by home team in last N
  - away_goals_scored_avg:        avg goals scored by away team in last N
  - away_goals_conceded_avg:      avg goals conceded by away team in last N
  - home_win_streak / away_win_streak: consecutive wins going into the match
  - h2h_home_wins / h2h_away_wins / h2h_draws: last N head-to-head results

Cold-start default: 0.0 for all features when a team has no prior matches.
"""

import pandas as pd
import numpy as np

LOOKBACK = 5
H2H_LOOKBACK = 5


def _team_recent_matches(df_finished: pd.DataFrame, team_id: int, before_date, n: int = LOOKBACK) -> pd.DataFrame:
    """Get the last `n` finished matches for a team before a given date."""
    mask = (
        ((df_finished["home_team_id"] == team_id) | (df_finished["away_team_id"] == team_id))
        & (df_finished["date"] < before_date)
    )
    return df_finished.loc[mask].sort_values("date", ascending=False).head(n)


def _compute_form(recent: pd.DataFrame, team_id: int) -> float:
    """Points earned: W=3, D=1, L=0."""
    if recent.empty:
        return 0.0
    points = 0.0
    for _, row in recent.iterrows():
        hg, ag = row["home_goals"], row["away_goals"]
        if pd.isna(hg) or pd.isna(ag):
            continue
        is_home = row["home_team_id"] == team_id
        if hg == ag:
            points += 1
        elif (is_home and hg > ag) or (not is_home and ag > hg):
            points += 3
    return points


def _compute_goals(recent: pd.DataFrame, team_id: int) -> tuple[float, float]:
    """Average (goals_scored, goals_conceded) in recent matches."""
    if recent.empty:
        return 0.0, 0.0
    scored, conceded = [], []
    for _, row in recent.iterrows():
        hg, ag = row["home_goals"], row["away_goals"]
        if pd.isna(hg) or pd.isna(ag):
            continue
        if row["home_team_id"] == team_id:
            scored.append(hg)
            conceded.append(ag)
        else:
            scored.append(ag)
            conceded.append(hg)
    if not scored:
        return 0.0, 0.0
    return float(np.mean(scored)), float(np.mean(conceded))


def _compute_win_streak(recent: pd.DataFrame, team_id: int) -> int:
    """Consecutive wins going into the match (most recent first)."""
    streak = 0
    for _, row in recent.iterrows():
        hg, ag = row["home_goals"], row["away_goals"]
        if pd.isna(hg) or pd.isna(ag):
            break
        is_home = row["home_team_id"] == team_id
        won = (is_home and hg > ag) or (not is_home and ag > hg)
        if won:
            streak += 1
        else:
            break
    return streak


def _compute_h2h(df_finished: pd.DataFrame, home_id: int, away_id: int, before_date, n: int = H2H_LOOKBACK) -> tuple[int, int, int]:
    """Returns (home_wins, away_wins, draws) from last N head-to-head meetings."""
    mask = (
        (
            ((df_finished["home_team_id"] == home_id) & (df_finished["away_team_id"] == away_id))
            | ((df_finished["home_team_id"] == away_id) & (df_finished["away_team_id"] == home_id))
        )
        & (df_finished["date"] < before_date)
    )
    h2h = df_finished.loc[mask].sort_values("date", ascending=False).head(n)

    hw, aw, dr = 0, 0, 0
    for _, row in h2h.iterrows():
        hg, ag = row["home_goals"], row["away_goals"]
        if pd.isna(hg) or pd.isna(ag):
            continue
        if hg == ag:
            dr += 1
        elif (row["home_team_id"] == home_id and hg > ag) or (row["away_team_id"] == home_id and ag > hg):
            hw += 1
        else:
            aw += 1
    return hw, aw, dr


FEATURE_COLUMNS = [
    "home_form", "away_form",
    "home_goals_scored_avg", "home_goals_conceded_avg",
    "away_goals_scored_avg", "away_goals_conceded_avg",
    "home_win_streak", "away_win_streak",
    "h2h_home_wins", "h2h_away_wins", "h2h_draws",
]


def build_features(df_all: pd.DataFrame, target_fixture_ids: list[int] | None = None) -> pd.DataFrame:
    """
    Build feature vectors for a set of fixtures.

    Args:
        df_all: DataFrame with columns [id, date, home_team_id, away_team_id, status, home_goals, away_goals].
        target_fixture_ids: If provided, only compute features for these fixtures.
                           If None, compute for all FT fixtures (training mode).

    Returns:
        DataFrame with fixture_id as index and feature columns.
    """
    df_all = df_all.copy()
    df_all["date"] = pd.to_datetime(df_all["date"], utc=True)
    df_all = df_all.sort_values("date")

    df_finished = df_all[df_all["status"] == "FT"].copy()

    if target_fixture_ids is not None:
        targets = df_all[df_all["id"].isin(target_fixture_ids)]
    else:
        targets = df_finished

    rows = []
    for _, fix in targets.iterrows():
        fid = fix["id"]
        home_id = fix["home_team_id"]
        away_id = fix["away_team_id"]
        match_date = fix["date"]

        home_recent = _team_recent_matches(df_finished, home_id, match_date)
        away_recent = _team_recent_matches(df_finished, away_id, match_date)

        home_form = _compute_form(home_recent, home_id)
        away_form = _compute_form(away_recent, away_id)

        hgs, hgc = _compute_goals(home_recent, home_id)
        ags, agc = _compute_goals(away_recent, away_id)

        hws = _compute_win_streak(home_recent, home_id)
        aws = _compute_win_streak(away_recent, away_id)

        h2h_hw, h2h_aw, h2h_dr = _compute_h2h(df_finished, home_id, away_id, match_date)

        rows.append({
            "fixture_id": fid,
            "home_form": home_form,
            "away_form": away_form,
            "home_goals_scored_avg": hgs,
            "home_goals_conceded_avg": hgc,
            "away_goals_scored_avg": ags,
            "away_goals_conceded_avg": agc,
            "home_win_streak": hws,
            "away_win_streak": aws,
            "h2h_home_wins": h2h_hw,
            "h2h_away_wins": h2h_aw,
            "h2h_draws": h2h_dr,
        })

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.set_index("fixture_id")
    return result
