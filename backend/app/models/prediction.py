from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture
    from app.models.team import Team


class Prediction(Base):
    __tablename__ = "predictions"

    fixture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fixtures.id", ondelete="CASCADE"), primary_key=True,
    )
    prob_home_win: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    prob_draw: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    prob_away_win: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    predicted_winner_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="SET NULL"),
    )
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    fixture: Mapped["Fixture"] = relationship(back_populates="prediction")
    predicted_winner: Mapped[Optional["Team"]] = relationship(back_populates="predictions")
