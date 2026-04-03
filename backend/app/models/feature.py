from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture


class Feature(Base):
    __tablename__ = "features"

    fixture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fixtures.id", ondelete="CASCADE"), primary_key=True,
    )
    home_team_form_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    away_team_form_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    home_win_streak: Mapped[Optional[int]] = mapped_column(Integer)
    away_win_streak: Mapped[Optional[int]] = mapped_column(Integer)
    home_avg_goals_scored: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    away_avg_goals_scored: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    home_avg_goals_conceded: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    away_avg_goals_conceded: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    implied_home_prob: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    implied_away_prob: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    fixture: Mapped["Fixture"] = relationship(back_populates="feature")
