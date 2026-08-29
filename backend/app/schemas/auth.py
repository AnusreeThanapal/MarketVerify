from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.app.schemas.common import BaseSchema


class UserProfile(BaseSchema):
    id: str = "demo-user-001"
    email: str = "analyst@marketverify.ai"
    full_name: str = "Chief Market Analyst"
    role: str = "LEAD_VERIFIER"
    is_active: bool = True


class LoginRequest(BaseSchema):
    email: str = "analyst@marketverify.ai"
    password: str = "password123"


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile
