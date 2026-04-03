from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TeamBase(BaseModel):
    id: int
    name: str
    logo_url: Optional[str] = None


class TeamResponse(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    country: Optional[str] = None
    founded: Optional[int] = None
    venue_name: Optional[str] = None
    created_at: datetime


class TeamBrief(TeamBase):
    """Lightweight team representation for embedding inside fixtures/standings."""
    model_config = ConfigDict(from_attributes=True)
