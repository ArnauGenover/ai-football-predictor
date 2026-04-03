from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture
    from app.models.injury import Injury
    from app.models.player import Player
    from app.models.prediction import Prediction
    from app.models.standing import Standing


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    founded: Mapped[Optional[int]] = mapped_column(Integer)
    venue_name: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    players: Mapped[list["Player"]] = relationship(back_populates="team")
    home_fixtures: Mapped[list["Fixture"]] = relationship(
        back_populates="home_team",
        foreign_keys="Fixture.home_team_id",
    )
    away_fixtures: Mapped[list["Fixture"]] = relationship(
        back_populates="away_team",
        foreign_keys="Fixture.away_team_id",
    )
    standings: Mapped[list["Standing"]] = relationship(back_populates="team")
    injuries: Mapped[list["Injury"]] = relationship(back_populates="team")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="predicted_winner")
