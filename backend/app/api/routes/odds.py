from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.models.odds import Odds
from app.schemas.odds import OddsResponse

router = APIRouter(prefix="/odds", tags=["Odds"])


@router.get("/{fixture_id}", response_model=list[OddsResponse])
async def get_odds_for_fixture(
    fixture_id: int,
    db: AsyncSession = DbSession,
):
    stmt = (
        select(Odds)
        .where(Odds.fixture_id == fixture_id)
        .order_by(Odds.updated_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No odds found for fixture {fixture_id}")

    return rows
