from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.fixture import Fixture
    from app.models.player import Player
    from app.models.team import Team


class Injury(Base):
    __tablename__ = "injuries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"),
    )
    fixture_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("fixtures.id", ondelete="CASCADE"),
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"),
    )
    type: Mapped[Optional[str]] = mapped_column(String(255))
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
    )

    player: Mapped[Optional["Player"]] = relationship(back_populates="injuries")
    fixture: Mapped[Optional["Fixture"]] = relationship(back_populates="injuries")
    team: Mapped[Optional["Team"]] = relationship(back_populates="injuries")
