"""initial_schema

Revision ID: 001
Revises:
Create Date: 2026-03-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. TEAMS
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country", sa.String(100)),
        sa.Column("logo_url", sa.String(500)),
        sa.Column("founded", sa.Integer),
        sa.Column("venue_name", sa.String(255)),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # 2. PLAYERS
    op.create_table(
        "players",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column(
            "team_id",
            sa.Integer,
            sa.ForeignKey("teams.id", ondelete="SET NULL"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("position", sa.String(50)),
        sa.Column("nationality", sa.String(100)),
        sa.Column("photo_url", sa.String(500)),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # 3. FIXTURES
    op.create_table(
        "fixtures",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column("league_id", sa.Integer, nullable=False),
        sa.Column("season", sa.Integer, nullable=False),
        sa.Column("date", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "home_team_id",
            sa.Integer,
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "away_team_id",
            sa.Integer,
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
        ),
        sa.Column("venue", sa.String(255)),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("referee", sa.String(255)),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # 4. RESULTS
    op.create_table(
        "results",
        sa.Column(
            "fixture_id",
            sa.Integer,
            sa.ForeignKey("fixtures.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("home_goals", sa.Integer),
        sa.Column("away_goals", sa.Integer),
        sa.Column("home_xg", sa.Numeric(5, 2)),
        sa.Column("away_xg", sa.Numeric(5, 2)),
        sa.Column("home_possession", sa.Integer),
        sa.Column("away_possession", sa.Integer),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # 5. STANDINGS
    op.create_table(
        "standings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("league_id", sa.Integer, nullable=False),
        sa.Column("season", sa.Integer, nullable=False),
        sa.Column(
            "team_id",
            sa.Integer,
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
        ),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column("points", sa.Integer, nullable=False),
        sa.Column("form", sa.String(20)),
        sa.Column("goals_diff", sa.Integer),
        sa.Column("played", sa.Integer),
        sa.Column("won", sa.Integer),
        sa.Column("draw", sa.Integer),
        sa.Column("lose", sa.Integer),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
        sa.UniqueConstraint("league_id", "season", "team_id"),
    )

    # 6. ODDS
    op.create_table(
        "odds",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "fixture_id",
            sa.Integer,
            sa.ForeignKey("fixtures.id", ondelete="CASCADE"),
        ),
        sa.Column("bookmaker", sa.String(100), nullable=False),
        sa.Column("home_win", sa.Numeric(6, 3), nullable=False),
        sa.Column("draw", sa.Numeric(6, 3), nullable=False),
        sa.Column("away_win", sa.Numeric(6, 3), nullable=False),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # 7. INJURIES
    op.create_table(
        "injuries",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "player_id",
            sa.Integer,
            sa.ForeignKey("players.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "fixture_id",
            sa.Integer,
            sa.ForeignKey("fixtures.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "team_id",
            sa.Integer,
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
        ),
        sa.Column("type", sa.String(255)),
        sa.Column("reason", sa.String(255)),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # 8. FEATURES
    op.create_table(
        "features",
        sa.Column(
            "fixture_id",
            sa.Integer,
            sa.ForeignKey("fixtures.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("home_team_form_score", sa.Numeric(5, 2)),
        sa.Column("away_team_form_score", sa.Numeric(5, 2)),
        sa.Column("home_win_streak", sa.Integer),
        sa.Column("away_win_streak", sa.Integer),
        sa.Column("home_avg_goals_scored", sa.Numeric(5, 2)),
        sa.Column("away_avg_goals_scored", sa.Numeric(5, 2)),
        sa.Column("home_avg_goals_conceded", sa.Numeric(5, 2)),
        sa.Column("away_avg_goals_conceded", sa.Numeric(5, 2)),
        sa.Column("implied_home_prob", sa.Numeric(5, 4)),
        sa.Column("implied_away_prob", sa.Numeric(5, 4)),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # 9. PREDICTIONS
    op.create_table(
        "predictions",
        sa.Column(
            "fixture_id",
            sa.Integer,
            sa.ForeignKey("fixtures.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("prob_home_win", sa.Numeric(5, 4), nullable=False),
        sa.Column("prob_draw", sa.Numeric(5, 4), nullable=False),
        sa.Column("prob_away_win", sa.Numeric(5, 4), nullable=False),
        sa.Column(
            "predicted_winner_id",
            sa.Integer,
            sa.ForeignKey("teams.id", ondelete="SET NULL"),
        ),
        sa.Column("model_version", sa.String(50)),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.current_timestamp(),
        ),
    )

    # INDEXES
    op.create_index("idx_fixtures_date", "fixtures", ["date"])
    op.create_index("idx_odds_fixture_id", "odds", ["fixture_id"])
    op.create_index("idx_standings_league_season", "standings", ["league_id", "season"])


def downgrade() -> None:
    op.drop_index("idx_standings_league_season", table_name="standings")
    op.drop_index("idx_odds_fixture_id", table_name="odds")
    op.drop_index("idx_fixtures_date", table_name="fixtures")

    op.drop_table("predictions")
    op.drop_table("features")
    op.drop_table("injuries")
    op.drop_table("odds")
    op.drop_table("standings")
    op.drop_table("results")
    op.drop_table("fixtures")
    op.drop_table("players")
    op.drop_table("teams")
