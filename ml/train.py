"""
Model training pipeline.

1. Fetch all FT fixtures + results from the database
2. Build feature vectors via features.py
3. Train a RandomForestClassifier (target: 0=Away, 1=Draw, 2=Home)
4. Save model.pkl and preprocessor.pkl
"""

import os
import sys
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import build_features, FEATURE_COLUMNS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "model.pkl"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"
MODEL_VERSION = "rf_v1"

DATABASE_URL = os.getenv("DATABASE_URL_SYNC")


def load_match_data() -> pd.DataFrame:
    """Fetch all fixtures with their results from the database."""
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
        df = pd.read_sql(query, conn)
    logger.info("Loaded %d fixtures (%d with results)", len(df), df["home_goals"].notna().sum())
    return df


def compute_target(row) -> int:
    """0 = Away Win, 1 = Draw, 2 = Home Win."""
    if row["home_goals"] > row["away_goals"]:
        return 2
    elif row["home_goals"] == row["away_goals"]:
        return 1
    else:
        return 0


def train():
    logger.info("Loading match data from database...")
    df_all = load_match_data()

    logger.info("Building features for finished matches...")
    df_features = build_features(df_all, target_fixture_ids=None)

    if df_features.empty:
        logger.error("No features computed — not enough finished matches.")
        sys.exit(1)

    # Align targets with features
    df_ft = df_all[df_all["status"] == "FT"].set_index("id")
    df_ft = df_ft.loc[df_features.index]
    df_ft["target"] = df_ft.apply(compute_target, axis=1)

    X = df_features[FEATURE_COLUMNS].values
    y = df_ft["target"].values

    # Drop rows with NaN features (shouldn't happen, but safety net)
    valid = ~np.isnan(X).any(axis=1)
    X, y = X[valid], y[valid]

    logger.info("Training set: %d samples, %d features", X.shape[0], X.shape[1])
    logger.info("Target distribution — Home: %d, Draw: %d, Away: %d",
                (y == 2).sum(), (y == 1).sum(), (y == 0).sum())

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    # Cross-validation
    scores = cross_val_score(clf, X_scaled, y, cv=5, scoring="accuracy")
    logger.info("5-fold CV accuracy: %.3f (+/- %.3f)", scores.mean(), scores.std())

    # Fit on full dataset
    clf.fit(X_scaled, y)

    # Feature importance
    importances = sorted(zip(FEATURE_COLUMNS, clf.feature_importances_), key=lambda x: -x[1])
    logger.info("Feature importances:")
    for name, imp in importances:
        logger.info("  %-28s %.4f", name, imp)

    # Save
    joblib.dump(clf, MODEL_PATH)
    joblib.dump({"scaler": scaler, "feature_columns": FEATURE_COLUMNS, "version": MODEL_VERSION}, PREPROCESSOR_PATH)
    logger.info("Model saved to %s", MODEL_PATH)
    logger.info("Preprocessor saved to %s", PREPROCESSOR_PATH)


if __name__ == "__main__":
    train()
