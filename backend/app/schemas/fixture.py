from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.team import TeamBrief


class FixtureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    league_id: int
    season: int
    date: datetime
    venue: Optional[str] = None
    status: str
    referee: Optional[str] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    home_team: Optional[TeamBrief] = None
    away_team: Optional[TeamBrief] = None
    created_at: datetime
