from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import EmailStr, Field
from backend.app.schemas.common import BaseSchema
from backend.app.models.user import UserRole


class UserBase(BaseSchema):
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserRead(UserBase):
    id: str
    created_at: datetime


class LoginRequest(BaseSchema):
    email: str
    password: str


class DemoLoginRequest(BaseSchema):
    role: UserRole


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class RawClaimRecord(BaseSchema):
    id: str
    raw_text: str
    language: str
    normalized_text: Optional[str] = None
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    source_handle: str
    submitted_at: datetime
    status: str


class RawAgentRunRecord(BaseSchema):
    id: str
    claim_id: str
    execution_trace: List[Dict[str, Any]]
    state_snapshot: Dict[str, Any]
    created_at: datetime


class RawQdrantDocRecord(BaseSchema):
    id: str
    collection_name: str
    payload: Dict[str, Any]
    text_snippet: Optional[str] = None
