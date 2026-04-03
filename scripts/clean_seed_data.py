"""
Remove all seed/synthetic fixtures (ID >= 9_000_000) and their predictions.
"""

import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "collector", ".env"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL_SYNC")


def clean():
    engine = create_engine(DATABASE_URL, echo=False)

    with engine.begin() as conn:
        pred_del = conn.execute(text("DELETE FROM predictions WHERE fixture_id >= 9000000"))
        fix_del = conn.execute(text("DELETE FROM fixtures WHERE id >= 9000000"))
        logger.info("Deleted %d seed predictions", pred_del.rowcount)
        logger.info("Deleted %d seed fixtures", fix_del.rowcount)

    with engine.connect() as conn:
        ns = conn.execute(text("SELECT COUNT(*) FROM fixtures WHERE status = 'NS'")).scalar()
        total = conn.execute(text("SELECT COUNT(*) FROM fixtures")).scalar()
        preds = conn.execute(text("SELECT COUNT(*) FROM predictions")).scalar()
        logger.info("Remaining — fixtures: %d (NS: %d), predictions: %d", total, ns, preds)


if __name__ == "__main__":
    clean()
