import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from backend.app.config import get_settings
from backend.app.core.logging import logger

settings = get_settings()

# Use SQLite local database for standalone local development if PostgreSQL is not available
db_url = settings.DATABASE_URL
if "postgresql" in db_url and not os.environ.get("USE_POSTGRES"):
    # Default to robust local SQLite file for standalone execution
    db_url = "sqlite+aiosqlite:///./marketverify.db"

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
