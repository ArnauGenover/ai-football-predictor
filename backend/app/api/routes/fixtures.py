from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import DbSession
from app.models.fixture import Fixture
from app.schemas.fixture import FixtureResponse

router = APIRouter(prefix="/fixtures", tags=["Fixtures"])


@router.get("", response_model=list[FixtureResponse])
async def list_fixtures(
    db: AsyncSession = DbSession,
    league_id: Optional[int] = Query(None, description="Filter by league ID"),
    season: Optional[int] = Query(None, description="Filter by season year"),
    status: Optional[str] = Query(None, description="Filter by status (NS, FT, LIVE, etc.)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = (
        select(Fixture)
        .options(selectinload(Fixture.home_team), selectinload(Fixture.away_team))
        .order_by(Fixture.date.desc())
        .limit(limit)
        .offset(offset)
    )

    if league_id is not None:
        stmt = stmt.where(Fixture.league_id == league_id)
    if season is not None:
        stmt = stmt.where(Fixture.season == season)
    if status is not None:
        stmt = stmt.where(Fixture.status == status)

    result = await db.execute(stmt)
    return result.scalars().all()
