#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════
# Football Analytics — Daily Update Pipeline
#
# Usage: sudo bash update_predictions.sh
#
# Steps:
#   1. Run the data collector (fetch fixtures from API)
#   2. Seed demo upcoming fixtures (if no real NS found)
#   3. Run ML predictions on NS fixtures
#   4. Restart backend to clear cache
# ═══════════════════════════════════════════════════

echo ""
echo "========================================"
echo "  Football Analytics Pipeline"
echo "  $(date)"
echo "========================================"

# Step 1: Collect data from API-Football
echo ""
echo "[1/4] Running data collector..."
docker compose run --rm --build collector

# Step 2: Check if we have NS fixtures; if not, seed demo data
echo ""
echo "[2/4] Checking for upcoming (NS) fixtures..."
NS_COUNT=$(docker compose run --rm ml-train python -c "
import os; from sqlalchemy import create_engine, text; from dotenv import load_dotenv
load_dotenv()
e = create_engine(os.getenv('DATABASE_URL_SYNC'))
with e.connect() as c: print(c.execute(text(\"SELECT COUNT(*) FROM fixtures WHERE status='NS'\")).scalar())
" 2>/dev/null | tail -1)

echo "  Found $NS_COUNT upcoming fixtures"

if [ "$NS_COUNT" = "0" ] || [ -z "$NS_COUNT" ]; then
    echo "  No real NS fixtures (free API tier). Seeding demo matches..."
    docker compose run --rm ml-train python seed_upcoming.py
fi

# Step 3: Run ML predictions
echo ""
echo "[3/4] Generating ML predictions..."
docker compose run --rm ml-train python predict.py

# Step 4: Restart backend to clear any cached responses
echo ""
echo "[4/4] Restarting backend..."
docker compose restart backend

echo ""
echo "========================================"
echo "  Pipeline complete!"
echo "  View predictions at:"
echo "    API:      http://localhost:7860/predictions"
echo "    Frontend: http://localhost:3000"
echo "========================================"
