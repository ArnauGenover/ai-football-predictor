"""
Football data collection pipeline.
Runs from GitHub Actions twice daily. Respects 100 req/day API-Football limit.

Budget per run (5 leagues):
  - 5 fixture calls (one per league, covers past 7 days + next 21 days)
  - N odds calls (only for NS matches within 48 hours)
  - Worst case ~25 total calls → 50/day with 2 runs → well under 100
"""

import os
import sys
import logging
import requests
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY,
}

TARGET_LEAGUES = [
    int(x) for x in os.getenv("TARGET_LEAGUE_IDS", "39,140,135,78,61").split(",")
]
CURRENT_SEASON = int(os.getenv("CURRENT_SEASON", "2024"))

DATABASE_URL = os.getenv("DATABASE_URL_SYNC")
HF_SPACE_URL = os.getenv("HF_SPACE_URL", "")


def get_engine():
    if not DATABASE_URL:
        logger.error("DATABASE_URL_SYNC is not set — check your .env file")
        sys.exit(1)
    safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    logger.info("Connecting to database: ...@%s", safe_url)
    return create_engine(DATABASE_URL, echo=False)


def api_get(endpoint: str, params: dict) -> dict:
    """Central API caller with debug logging."""
    url = f"{BASE_URL}/{endpoint}"
    logger.info("  API → GET /%s  params=%s", endpoint, params)
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    results_count = len(data.get("response", []))
    errors = data.get("errors", {})
    remaining = data.get("paging", {}).get("total", "?")
    logger.info("  API ← %d results (total pages: %s)", results_count, remaining)

    if errors:
        logger.warning("  API errors: %s", errors)

    return data


def fetch_fixtures(league_id: int, season: int) -> list:
    """Fetches ALL fixtures for a league+season (no date filter)."""
    params = {"league": league_id, "season": season}
    data = api_get("fixtures", params)
    return data.get("response", [])


def fetch_match_odds(fixture_id: int) -> list:
    """Fetches pre-match odds for a specific fixture (Bet365 only)."""
    params = {"fixture": fixture_id, "bookmaker": 8}
    data = api_get("odds", params)
    return data.get("response", [])


UPSERT_TEAM_SQL = text("""
    INSERT INTO teams (id, name, logo_url)
    VALUES (:id, :name, :logo_url)
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        logo_url = EXCLUDED.logo_url
""")

UPSERT_FIXTURE_SQL = text("""
    INSERT INTO fixtures (id, league_id, season, date, home_team_id, away_team_id,
                          venue, status, referee)
    VALUES (:id, :league_id, :season, :date, :home_team_id, :away_team_id,
            :venue, :status, :referee)
    ON CONFLICT (id) DO UPDATE SET
        status   = EXCLUDED.status,
        date     = EXCLUDED.date,
        venue    = EXCLUDED.venue,
        referee  = EXCLUDED.referee
""")

UPSERT_RESULT_SQL = text("""
    INSERT INTO results (fixture_id, home_goals, away_goals)
    VALUES (:fixture_id, :home_goals, :away_goals)
    ON CONFLICT (fixture_id) DO UPDATE SET
        home_goals = EXCLUDED.home_goals,
        away_goals = EXCLUDED.away_goals,
        updated_at = CURRENT_TIMESTAMP
""")

DELETE_OLD_ODDS_SQL = text("""
    DELETE FROM odds WHERE fixture_id = :fixture_id AND bookmaker = :bookmaker
""")

INSERT_ODDS_SQL = text("""
    INSERT INTO odds (fixture_id, bookmaker, home_win, draw, away_win)
    VALUES (:fixture_id, :bookmaker, :home_win, :draw, :away_win)
""")


def run_pipeline():
    logger.info("Starting data collection pipeline...")
    logger.info("Season: %d | Leagues: %s", CURRENT_SEASON, TARGET_LEAGUES)
    engine = get_engine()
    api_call_count = 0
    now = datetime.now(timezone.utc)
    total_fixtures = 0

    with engine.begin() as conn:
        for league in TARGET_LEAGUES:
            logger.info("── League %s (season %s) ──", league, CURRENT_SEASON)
            fixtures = fetch_fixtures(league, CURRENT_SEASON)
            api_call_count += 1

            if not fixtures:
                logger.warning("  No fixtures returned for league %s — skipping", league)
                continue

            logger.info("  Processing %d fixtures...", len(fixtures))

            for item in fixtures:
                fixture_data = item["fixture"]
                teams_data = item["teams"]
                goals_data = item.get("goals", {})
                fixture_id = fixture_data["id"]
                total_fixtures += 1

                # Upsert Teams
                for side in ("home", "away"):
                    team = teams_data[side]
                    conn.execute(UPSERT_TEAM_SQL, {
                        "id": team["id"],
                        "name": team["name"],
                        "logo_url": team.get("logo"),
                    })

                # Upsert Fixture
                venue_info = fixture_data.get("venue") or {}
                conn.execute(UPSERT_FIXTURE_SQL, {
                    "id": fixture_id,
                    "league_id": league,
                    "season": CURRENT_SEASON,
                    "date": fixture_data["date"],
                    "home_team_id": teams_data["home"]["id"],
                    "away_team_id": teams_data["away"]["id"],
                    "venue": venue_info.get("name"),
                    "status": fixture_data["status"]["short"],
                    "referee": fixture_data.get("referee"),
                })

                # Upsert Result if match is finished
                status = fixture_data["status"]["short"]
                if status == "FT" and goals_data.get("home") is not None:
                    conn.execute(UPSERT_RESULT_SQL, {
                        "fixture_id": fixture_id,
                        "home_goals": goals_data["home"],
                        "away_goals": goals_data["away"],
                    })

                # Fetch & insert odds (48-hour window, upcoming only)
                match_date = datetime.fromisoformat(
                    fixture_data["date"].replace("Z", "+00:00")
                )
                is_upcoming = status == "NS"
                within_48h = (match_date - now).total_seconds() <= 48 * 3600

                if is_upcoming and within_48h:
                    logger.info(
                        "  Fetching odds: %s vs %s...",
                        teams_data["home"]["name"],
                        teams_data["away"]["name"],
                    )
                    odds_data = fetch_match_odds(fixture_id)
                    api_call_count += 1

                    if odds_data and odds_data[0].get("bookmakers"):
                        bookmakers = odds_data[0]["bookmakers"]
                        if bookmakers:
                            bets = bookmakers[0]["bets"]
                            match_winner_bet = next(
                                (b for b in bets if b["id"] == 1), None
                            )
                            if match_winner_bet:
                                values = {
                                    v["value"]: float(v["odd"])
                                    for v in match_winner_bet["values"]
                                }
                                bookmaker_name = bookmakers[0].get("name", "Bet365")

                                conn.execute(DELETE_OLD_ODDS_SQL, {
                                    "fixture_id": fixture_id,
                                    "bookmaker": bookmaker_name,
                                })
                                conn.execute(INSERT_ODDS_SQL, {
                                    "fixture_id": fixture_id,
                                    "bookmaker": bookmaker_name,
                                    "home_win": values.get("Home", 0),
                                    "draw": values.get("Draw", 0),
                                    "away_win": values.get("Away", 0),
                                })
                                logger.info(
                                    "    Odds saved: H=%.2f  D=%.2f  A=%.2f",
                                    values.get("Home", 0),
                                    values.get("Draw", 0),
                                    values.get("Away", 0),
                                )

                    time.sleep(6.5)

    logger.info("Processed %d total fixtures across %d leagues", total_fixtures, len(TARGET_LEAGUES))

    # Verify data was persisted
    with engine.connect() as verify_conn:
        team_count = verify_conn.execute(text("SELECT COUNT(*) FROM teams")).scalar()
        fixture_count = verify_conn.execute(text("SELECT COUNT(*) FROM fixtures")).scalar()
        result_count = verify_conn.execute(text("SELECT COUNT(*) FROM results")).scalar()
        logger.info("DB totals — teams: %d, fixtures: %d, results: %d", team_count, fixture_count, result_count)

    # Ping Hugging Face Space to prevent sleep
    if HF_SPACE_URL:
        try:
            resp = requests.get(f"{HF_SPACE_URL}/health", timeout=15)
            logger.info("HF Space keep-alive ping: %s", resp.status_code)
        except Exception as exc:
            logger.warning("HF Space ping failed: %s", exc)

    logger.info(
        "Pipeline finished. API calls this run: %d / 100 daily budget",
        api_call_count,
    )


if __name__ == "__main__":
    run_pipeline()
