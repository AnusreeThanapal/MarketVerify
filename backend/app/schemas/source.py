from datetime import datetime
from typing import Optional, List
from pydantic import Field
from backend.app.schemas.common import BaseSchema


class SourceTrajectoryItem(BaseSchema):
    id: str
    source_handle: str
    source_name: Optional[str] = None
    past_claim_text: str
    ticker: Optional[str] = None
    was_accurate: bool
    lag_hours: Optional[int] = None
    category: str
    outcome_summary: str
    outcome_date: datetime
    recorded_at: datetime


class SourceTrustHistory(BaseSchema):
    source_handle: str
    total_claims_evaluated: int
    accurate_claims_count: int
    accuracy_rate: float
    trust_score: float
    confidence_level: str
    category_breakdown: dict = Field(default_factory=dict)
    recent_trajectories: List[SourceTrajectoryItem] = Field(default_factory=list)
