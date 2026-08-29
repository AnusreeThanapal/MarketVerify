import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Float, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class SourceTrajectory(Base):
    __tablename__ = "source_trajectories"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source_handle: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    past_claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    ticker: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    was_accurate: Mapped[bool] = mapped_column(Boolean, nullable=False)
    lag_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="rumor", nullable=False)
    outcome_summary: Mapped[str] = mapped_column(Text, nullable=False)
    outcome_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
