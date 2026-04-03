from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture


class Odds(Base):
    __tablename__ = "odds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fixture_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("fixtures.id", ondelete="CASCADE"),
    )
    bookmaker: Mapped[str] = mapped_column(String(100), nullable=False)
    home_win: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    draw: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    away_win: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    fixture: Mapped[Optional["Fixture"]] = relationship(back_populates="odds")
