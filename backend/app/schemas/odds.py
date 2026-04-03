from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OddsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fixture_id: Optional[int] = None
    bookmaker: str
    home_win: float
    draw: float
    away_win: float
    updated_at: datetime
