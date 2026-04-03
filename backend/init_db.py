"""
Create all tables in the connected database (Neon or local).
Run via: docker compose exec backend python init_db.py
"""

import asyncio

from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401 — registers all 9 tables with Base.metadata


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Tables created successfully in the database.")


if __name__ == "__main__":
    asyncio.run(init_models())
