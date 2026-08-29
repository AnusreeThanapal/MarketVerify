from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.config import get_settings
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, create_access_token
from backend.app.models.user import User
from backend.app.schemas.user import LoginRequest, DemoLoginRequest, TokenResponse, UserRead
from backend.app.api.deps import get_current_user

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with Database Credentials",
    description="Authenticates against the users table using bcrypt and issues a signed JWT access token with user role claims.",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    # 1. Query user from database
    query = select(User).where(User.email == payload.email.strip().lower())
    res = await db.execute(query)
    user = res.scalar_one_or_none()

    # 2. Verify existence and password hash
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please verify credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    # 3. Create signed JWT token with role in payload
    token = create_access_token(
        subject=user.email,
        role=user.role.value,
        user_id=user.id,
        full_name=user.full_name,
    )

    user_read = UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_read,
    )


@router.post(
    "/demo-login",
    response_model=TokenResponse,
    summary="1-Click Demo Login by Role",
    description="Authenticates the requested demo role account without transmitting plaintext passwords over frontend code.",
)
async def demo_login(
    payload: DemoLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    # 1. Lookup demo user by role
    query = select(User).where(User.role == payload.role).where(User.is_active == True)
    res = await db.execute(query)
    user = res.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active demo account found for role {payload.role.value}.",
        )

    # 2. Generate token
    token = create_access_token(
        subject=user.email,
        role=user.role.value,
        user_id=user.id,
        full_name=user.full_name,
    )

    user_read = UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_read,
    )


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get Current Authenticated User",
    description="Returns profile of the user verified via Bearer JWT token.",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
