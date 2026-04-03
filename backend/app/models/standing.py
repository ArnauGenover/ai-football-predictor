from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.team import Team


class Standing(Base):
    __tablename__ = "standings"
    __table_args__ = (
        UniqueConstraint("league_id", "season", "team_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    league_id: Mapped[int] = mapped_column(Integer, nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"),
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    form: Mapped[Optional[str]] = mapped_column(String(20))
    goals_diff: Mapped[Optional[int]] = mapped_column(Integer)
    played: Mapped[Optional[int]] = mapped_column(Integer)
    won: Mapped[Optional[int]] = mapped_column(Integer)
    draw: Mapped[Optional[int]] = mapped_column(Integer)
    lose: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    team: Mapped[Optional["Team"]] = relationship(back_populates="standings")
