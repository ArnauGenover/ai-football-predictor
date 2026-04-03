from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession
from app.models.prediction import Prediction
from app.models.fixture import Fixture
from app.schemas.prediction import PredictionWithFixture

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("", response_model=list[PredictionWithFixture])
async def list_predictions(
    db: AsyncSession = DbSession,
    league_id: Optional[int] = Query(None, description="Filter by league ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = (
        select(Prediction)
        .join(Fixture, Prediction.fixture_id == Fixture.id)
        .options(
            selectinload(Prediction.fixture).selectinload(Fixture.home_team),
            selectinload(Prediction.fixture).selectinload(Fixture.away_team),
        )
        .order_by(Fixture.date.desc())
        .limit(limit)
        .offset(offset)
    )

    if league_id is not None:
        stmt = stmt.where(Fixture.league_id == league_id)

    result = await db.execute(stmt)
    predictions = result.scalars().all()

    return [
        PredictionWithFixture(
            fixture_id=p.fixture_id,
            prob_home_win=float(p.prob_home_win),
            prob_draw=float(p.prob_draw),
            prob_away_win=float(p.prob_away_win),
            predicted_winner_id=p.predicted_winner_id,
            model_version=p.model_version,
            created_at=p.created_at,
            fixture_date=p.fixture.date if p.fixture else None,
            league_id=p.fixture.league_id if p.fixture else None,
            status=p.fixture.status if p.fixture else None,
            home_team=p.fixture.home_team if p.fixture else None,
            away_team=p.fixture.away_team if p.fixture else None,
        )
        for p in predictions
    ]
