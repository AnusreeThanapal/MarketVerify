import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from backend.app.core.database import Base


class ClaimStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True, nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=True)
    source_handle: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    status: Mapped[ClaimStatus] = mapped_column(
        SQLEnum(ClaimStatus, name="claim_status_enum", native_enum=False),
        default=ClaimStatus.PENDING,
        nullable=False,
    )

    # Relationships
    verdict: Mapped["Verdict"] = relationship(
        "Verdict", back_populates="claim", uselist=False, cascade="all, delete-orphan"
    )
    run_logs: Mapped[list["AgentRunLog"]] = relationship(
        "AgentRunLog", back_populates="claim", cascade="all, delete-orphan"
    )
