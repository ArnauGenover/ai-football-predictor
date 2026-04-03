from fastapi import APIRouter

from app.api.routes.teams import router as teams_router
from app.api.routes.fixtures import router as fixtures_router
from app.api.routes.odds import router as odds_router
from app.api.routes.standings import router as standings_router
from app.api.routes.predictions import router as predictions_router

api_router = APIRouter()
api_router.include_router(teams_router)
api_router.include_router(fixtures_router)
api_router.include_router(odds_router)
api_router.include_router(standings_router)
api_router.include_router(predictions_router)
