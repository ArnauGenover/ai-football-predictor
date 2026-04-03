from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture


class Result(Base):
    __tablename__ = "results"

    fixture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fixtures.id", ondelete="CASCADE"), primary_key=True,
    )
    home_goals: Mapped[Optional[int]] = mapped_column(Integer)
    away_goals: Mapped[Optional[int]] = mapped_column(Integer)
    home_xg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    away_xg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    home_possession: Mapped[Optional[int]] = mapped_column(Integer)
    away_possession: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    fixture: Mapped["Fixture"] = relationship(back_populates="result")
