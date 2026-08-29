from datetime import datetime, timezone
from typing import Optional, List
from pydantic import Field
from backend.app.schemas.common import BaseSchema
from backend.app.models.claim import ClaimStatus
from backend.app.models.verdict import VerdictStatus, SentimentLabel
from backend.app.schemas.trace import TraceEntry


class ClaimCreate(BaseSchema):
    raw_text: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Raw text of the rumor or claim (English or Tamil)",
        examples=["Reliance Industries in talks to acquire 40% stake in quick commerce app Zepto."],
    )
    source_handle: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Handle or identifier of the source (e.g. @dalalstreetinsider, CNBC_Rumors)",
        examples=["@dalalstreetinsider"],
    )
    language: Optional[str] = Field(
        default=None,
        description="Optional language code ('en' or 'ta'). Auto-detected if omitted.",
        examples=["en"],
    )
    ticker: Optional[str] = Field(
        default=None,
        description="Optional stock ticker (e.g. RELIANCE, TATASTEEL). Extracted automatically if omitted.",
        examples=["RELIANCE"],
    )


class CitationItem(BaseSchema):
    doc_id: str
    filing_type: str
    filing_date: str
    headline: str
    similarity_score: float
    snippet: str
    source_url: Optional[str] = None


class VerdictResponse(BaseSchema):
    id: str
    claim_id: str
    verdict_status: VerdictStatus
    confidence_score: float
    trust_score: float
    trust_rationale: Optional[str] = None
    verification_status: str
    citations: List[CitationItem] = Field(default_factory=list)
    sentiment: SentimentLabel
    lead_lag_note: Optional[str] = None
    explanation: str
    created_at: datetime


class ClaimResponse(BaseSchema):
    id: str
    raw_text: str
    language: str
    normalized_text: Optional[str] = None
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    source_handle: str
    submitted_at: datetime
    status: ClaimStatus
    verdict: Optional[VerdictResponse] = None
    trace: Optional[List[TraceEntry]] = None


class ClaimSummary(BaseSchema):
    id: str
    raw_text: str
    language: str
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    source_handle: str
    submitted_at: datetime
    status: ClaimStatus
    verdict_status: Optional[VerdictStatus] = None
    confidence_score: Optional[float] = None
