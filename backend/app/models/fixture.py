from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.feature import Feature
    from app.models.injury import Injury
    from app.models.odds import Odds
    from app.models.prediction import Prediction
    from app.models.result import Result
    from app.models.team import Team


class Fixture(Base):
    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    league_id: Mapped[int] = mapped_column(Integer, nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=False)
    home_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"),
    )
    away_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"),
    )
    venue: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    referee: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    home_team: Mapped[Optional["Team"]] = relationship(
        back_populates="home_fixtures",
        foreign_keys=[home_team_id],
    )
    away_team: Mapped[Optional["Team"]] = relationship(
        back_populates="away_fixtures",
        foreign_keys=[away_team_id],
    )
    result: Mapped[Optional["Result"]] = relationship(
        back_populates="fixture", uselist=False,
    )
    odds: Mapped[list["Odds"]] = relationship(back_populates="fixture")
    injuries: Mapped[list["Injury"]] = relationship(back_populates="fixture")
    feature: Mapped[Optional["Feature"]] = relationship(
        back_populates="fixture", uselist=False,
    )
    prediction: Mapped[Optional["Prediction"]] = relationship(
        back_populates="fixture", uselist=False,
    )
