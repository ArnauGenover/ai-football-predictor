"""
Prediction engine.

1. Load model.pkl and preprocessor.pkl
2. Fetch all NS (Not Started) fixtures from the database
3. Build features for those fixtures
4. Predict probabilities for Home Win, Draw, Away Win
5. Write predictions to the predictions table
"""

import os
import sys
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import build_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "model.pkl"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"

DATABASE_URL = os.getenv("DATABASE_URL_SYNC")


def load_all_fixtures() -> pd.DataFrame:
    engine = create_engine(DATABASE_URL, echo=False)
    query = text("""
        SELECT
            f.id, f.date, f.home_team_id, f.away_team_id, f.status, f.league_id,
            r.home_goals, r.away_goals
        FROM fixtures f
        LEFT JOIN results r ON r.fixture_id = f.id
        ORDER BY f.date
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def predict():
    if not MODEL_PATH.exists():
        logger.error("model.pkl not found — run train.py first")
        sys.exit(1)

    clf = joblib.load(MODEL_PATH)
    meta = joblib.load(PREPROCESSOR_PATH)
    scaler = meta["scaler"]
    feature_columns = meta["feature_columns"]
    version = meta["version"]

    logger.info("Loaded model version: %s", version)

    df_all = load_all_fixtures()
    ns_ids = df_all[df_all["status"] == "NS"]["id"].tolist()

    if not ns_ids:
        logger.warning("No upcoming (NS) fixtures found — nothing to predict.")
        return

    logger.info("Building features for %d upcoming fixtures...", len(ns_ids))
    df_features = build_features(df_all, target_fixture_ids=ns_ids)

    if df_features.empty:
        logger.warning("Could not compute features for any upcoming fixture.")
        return

    X = df_features[feature_columns].values
    X_scaled = scaler.transform(X)

    # class order: [0=Away, 1=Draw, 2=Home]
    probas = clf.predict_proba(X_scaled)

    # Map class indices to column positions
    class_to_idx = {c: i for i, c in enumerate(clf.classes_)}
    idx_away = class_to_idx.get(0, 0)
    idx_draw = class_to_idx.get(1, 1)
    idx_home = class_to_idx.get(2, 2)

    # Build prediction rows
    fixture_ids = df_features.index.tolist()
    df_ns = df_all.set_index("id").loc[fixture_ids]

    engine = create_engine(DATABASE_URL, echo=False)
    upsert_sql = text("""
        INSERT INTO predictions (fixture_id, prob_home_win, prob_draw, prob_away_win,
                                 predicted_winner_id, model_version)
        VALUES (:fixture_id, :prob_home_win, :prob_draw, :prob_away_win,
                :predicted_winner_id, :model_version)
        ON CONFLICT (fixture_id) DO UPDATE SET
            prob_home_win = EXCLUDED.prob_home_win,
            prob_draw = EXCLUDED.prob_draw,
            prob_away_win = EXCLUDED.prob_away_win,
            predicted_winner_id = EXCLUDED.predicted_winner_id,
            model_version = EXCLUDED.model_version,
            created_at = CURRENT_TIMESTAMP
    """)

    with engine.begin() as conn:
        for i, fid in enumerate(fixture_ids):
            p_home = float(probas[i][idx_home])
            p_draw = float(probas[i][idx_draw])
            p_away = float(probas[i][idx_away])

            # Determine predicted winner
            row = df_ns.loc[fid]
            pred_class = int(np.argmax([p_away, p_draw, p_home]))
            if pred_class == 2:
                winner_id = int(row["home_team_id"])
            elif pred_class == 0:
                winner_id = int(row["away_team_id"])
            else:
                winner_id = None

            conn.execute(upsert_sql, {
                "fixture_id": fid,
                "prob_home_win": round(p_home, 4),
                "prob_draw": round(p_draw, 4),
                "prob_away_win": round(p_away, 4),
                "predicted_winner_id": winner_id,
                "model_version": version,
            })

            logger.info(
                "  Fixture %d: Home=%.1f%% Draw=%.1f%% Away=%.1f%%",
                fid, p_home * 100, p_draw * 100, p_away * 100,
            )

    logger.info("Saved %d predictions to database.", len(fixture_ids))


if __name__ == "__main__":
    predict()
