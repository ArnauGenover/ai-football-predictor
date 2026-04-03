from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.models.team import Team
from app.schemas.team import TeamResponse

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("", response_model=list[TeamResponse])
async def list_teams(
    db: AsyncSession = DbSession,
    search: Optional[str] = Query(None, description="Search teams by name"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Team).order_by(Team.name).limit(limit).offset(offset)

    if search:
        stmt = stmt.where(func.lower(Team.name).contains(search.lower()))

    result = await db.execute(stmt)
    return result.scalars().all()
