from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.team import TeamBrief


class StandingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    league_id: int
    season: int
    rank: int
    points: int
    form: Optional[str] = None
    goals_diff: Optional[int] = None
    played: Optional[int] = None
    won: Optional[int] = None
    draw: Optional[int] = None
    lose: Optional[int] = None
    team_id: Optional[int] = None
    team: Optional[TeamBrief] = None
    updated_at: datetime
