import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from backend.app.core.database import Base


class VerdictStatus(str, enum.Enum):
    CORROBORATED_OFFICIAL = "CORROBORATED_OFFICIAL"
    LIKELY_CREDIBLE = "LIKELY_CREDIBLE"
    UNVERIFIED_RUMOR = "UNVERIFIED_RUMOR"
    CONTRADICTED_BY_FILING = "CONTRADICTED_BY_FILING"
    DEBUNKED_FALSEHOOD = "DEBUNKED_FALSEHOOD"
    NO_EVIDENCE_FOUND = "NO_EVIDENCE_FOUND"


class SentimentLabel(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class Verdict(Base):
    __tablename__ = "verdicts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    claim_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("claims.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    
    verdict_status: Mapped[VerdictStatus] = mapped_column(
        SQLEnum(VerdictStatus, name="verdict_status_enum", native_enum=False),
        nullable=False,
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Trust evaluation components
    trust_score: Mapped[float] = mapped_column(Float, nullable=False)
    trust_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Verification details
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False)
    citations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    # Sentiment & Market dynamics
    sentiment: Mapped[SentimentLabel] = mapped_column(
        SQLEnum(SentimentLabel, name="sentiment_label_enum", native_enum=False),
        default=SentimentLabel.NEUTRAL,
        nullable=False,
    )
    lead_lag_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Final synthesized summary
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    claim: Mapped["Claim"] = relationship("Claim", back_populates="verdict")
