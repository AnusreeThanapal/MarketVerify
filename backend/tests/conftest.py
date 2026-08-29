import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.models.source_trajectory import SourceTrajectory
from datetime import datetime, timezone
import uuid

# In-memory SQLite async engine for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

TestingAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingAsyncSessionLocal() as session:
        # Seed test source trajectories
        traj1 = SourceTrajectory(
            id=str(uuid.uuid4()),
            source_handle="@dalalstreetinsider",
            source_name="Dalal Street Insider",
            past_claim_text="Reliance Retail expanding to quick commerce",
            ticker="RELIANCE",
            was_accurate=True,
            lag_hours=48,
            category="expansion",
            outcome_summary="Confirmed by exchange disclosure",
            outcome_date=datetime.now(timezone.utc),
            recorded_at=datetime.now(timezone.utc),
        )
        traj2 = SourceTrajectory(
            id=str(uuid.uuid4()),
            source_handle="@dalalstreetinsider",
            source_name="Dalal Street Insider",
            past_claim_text="Tata Steel Hydrogen Plant approval",
            ticker="TATASTEEL",
            was_accurate=True,
            lag_hours=24,
            category="capex",
            outcome_summary="Confirmed on NSE",
            outcome_date=datetime.now(timezone.utc),
            recorded_at=datetime.now(timezone.utc),
        )
        traj3 = SourceTrajectory(
            id=str(uuid.uuid4()),
            source_handle="@fake_breakout_bot",
            source_name="Fake Bot",
            past_claim_text="SBI 1:5 bonus share issue",
            ticker="SBIN",
            was_accurate=False,
            lag_hours=120,
            category="corporate_action",
            outcome_summary="Refuted by bank",
            outcome_date=datetime.now(timezone.utc),
            recorded_at=datetime.now(timezone.utc),
        )
        session.add_all([traj1, traj2, traj3])
        await session.commit()

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
