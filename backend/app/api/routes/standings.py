from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession
from app.models.standing import Standing
from app.schemas.standing import StandingResponse

router = APIRouter(prefix="/standings", tags=["Standings"])


@router.get("/{league_id}", response_model=list[StandingResponse])
async def get_standings(
    league_id: int,
    db: AsyncSession = DbSession,
    season: Optional[int] = Query(None, description="Filter by season year (defaults to latest)"),
):
    stmt = (
        select(Standing)
        .options(selectinload(Standing.team))
        .where(Standing.league_id == league_id)
        .order_by(Standing.rank)
    )

    if season is not None:
        stmt = stmt.where(Standing.season == season)
    else:
        # Default to the latest available season for this league
        latest_season_subq = (
            select(Standing.season)
            .where(Standing.league_id == league_id)
            .order_by(Standing.season.desc())
            .limit(1)
            .scalar_subquery()
        )
        stmt = stmt.where(Standing.season == latest_season_subq)

    result = await db.execute(stmt)
    return result.scalars().all()
