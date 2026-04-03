from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.team import TeamBrief


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fixture_id: int
    prob_home_win: float
    prob_draw: float
    prob_away_win: float
    predicted_winner_id: Optional[int] = None
    model_version: Optional[str] = None
    created_at: datetime


class PredictionWithFixture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fixture_id: int
    prob_home_win: float
    prob_draw: float
    prob_away_win: float
    predicted_winner_id: Optional[int] = None
    model_version: Optional[str] = None
    created_at: datetime

    # Fixture info (joined)
    fixture_date: Optional[datetime] = None
    league_id: Optional[int] = None
    status: Optional[str] = None
    home_team: Optional[TeamBrief] = None
    away_team: Optional[TeamBrief] = None
