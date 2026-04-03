"""
Seed realistic upcoming (NS) fixtures into the database using teams we already have.
This is needed because the free API-Football plan only covers seasons 2022-2024,
and all those matches are already finished.

These fixtures use real team IDs from our DB with future dates so the prediction
pipeline has something to work with.
"""

import os
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL_SYNC")

# Realistic matchday fixtures using real team IDs from the 2024 season data.
# fixture IDs use 9_000_000+ range to avoid collisions with real API-Football IDs.
UPCOMING_FIXTURES = [
    # Premier League (39)
    {"id": 9000001, "league_id": 39, "home": 42, "away": 49, "venue": "Emirates Stadium"},        # Arsenal vs Chelsea
    {"id": 9000002, "league_id": 39, "home": 33, "away": 40, "venue": "Old Trafford"},             # Man Utd vs Liverpool
    {"id": 9000003, "league_id": 39, "home": 50, "away": 47, "venue": "Etihad Stadium"},           # Man City vs Tottenham
    {"id": 9000004, "league_id": 39, "home": 66, "away": 34, "venue": "Villa Park"},               # Aston Villa vs Newcastle
    # La Liga (140)
    {"id": 9000005, "league_id": 140, "home": 529, "away": 541, "venue": "Santiago Bernabéu"},     # Real Madrid vs Barcelona
    {"id": 9000006, "league_id": 140, "home": 530, "away": 548, "venue": "Civitas Metropolitano"}, # Atletico vs Real Sociedad
    {"id": 9000007, "league_id": 140, "home": 543, "away": 532, "venue": "San Mamés"},             # Athletic vs Real Betis
    # Serie A (135)
    {"id": 9000008, "league_id": 135, "home": 489, "away": 505, "venue": "San Siro"},              # AC Milan vs Inter
    {"id": 9000009, "league_id": 135, "home": 496, "away": 497, "venue": "Allianz Stadium"},       # Juventus vs Roma
    {"id": 9000010, "league_id": 135, "home": 492, "away": 500, "venue": "Diego Armando Maradona"},# Napoli vs Atalanta
    # Bundesliga (78)
    {"id": 9000011, "league_id": 78, "home": 157, "away": 165, "venue": "Allianz Arena"},          # Bayern vs Dortmund
    {"id": 9000012, "league_id": 78, "home": 173, "away": 168, "venue": "Red Bull Arena"},         # RB Leipzig vs Leverkusen
    # Ligue 1 (61)
    {"id": 9000013, "league_id": 61, "home": 85, "away": 81, "venue": "Parc des Princes"},         # PSG vs Marseille
    {"id": 9000014, "league_id": 61, "home": 79, "away": 80, "venue": "Groupama Stadium"},         # Lyon vs Monaco
]


def seed():
    engine = create_engine(DATABASE_URL, echo=False)
    now = datetime.now(timezone.utc)

    upsert_fixture = text("""
        INSERT INTO fixtures (id, league_id, season, date, home_team_id, away_team_id, venue, status)
        VALUES (:id, :league_id, :season, :date, :home_team_id, :away_team_id, :venue, :status)
        ON CONFLICT (id) DO UPDATE SET
            status = EXCLUDED.status,
            date = EXCLUDED.date
    """)

    with engine.begin() as conn:
        # Verify teams exist
        team_ids = set()
        for f in UPCOMING_FIXTURES:
            team_ids.add(f["home"])
            team_ids.add(f["away"])

        existing = conn.execute(
            text("SELECT id FROM teams WHERE id = ANY(:ids)"),
            {"ids": list(team_ids)},
        ).scalars().all()
        existing_set = set(existing)
        missing = team_ids - existing_set
        if missing:
            logger.warning("Some team IDs not in DB (will skip those fixtures): %s", missing)

        inserted = 0
        for i, f in enumerate(UPCOMING_FIXTURES):
            if f["home"] not in existing_set or f["away"] not in existing_set:
                continue

            match_date = now + timedelta(days=3 + i)

            conn.execute(upsert_fixture, {
                "id": f["id"],
                "league_id": f["league_id"],
                "season": 2024,
                "date": match_date.isoformat(),
                "home_team_id": f["home"],
                "away_team_id": f["away"],
                "venue": f["venue"],
                "status": "NS",
            })
            inserted += 1

        # Clean old predictions for these fixtures so predict.py re-generates them
        conn.execute(text("DELETE FROM predictions WHERE fixture_id >= 9000000"))

    logger.info("Seeded %d upcoming (NS) fixtures into the database.", inserted)

    # Verify
    with engine.connect() as conn:
        ns_count = conn.execute(text("SELECT COUNT(*) FROM fixtures WHERE status = 'NS'")).scalar()
        logger.info("Total NS fixtures in DB: %d", ns_count)


if __name__ == "__main__":
    seed()
