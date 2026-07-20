import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.dependencies import get_current_user
from src.core.security import create_access_token, get_password_hash, verify_password
from src.db.session import get_db
from src.models.user import RefreshToken, User, UserRole
from src.schemas.auth import LoginRequest, RegisterRequest, TokenPair
from src.schemas.user import UserRead

router = APIRouter()


def _create_refresh_token(user: User, db: AsyncSession) -> str:
    raw_refresh = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(raw_refresh),
        expires_at=expires_at,
    )
    db.add(refresh)
    return raw_refresh


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    await db.flush()

    db.add(UserRole(user_id=user.id, role="learner"))

    access_token = create_access_token({"sub": str(user.id)})
    raw_refresh = _create_refresh_token(user, db)
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=raw_refresh)


@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    raw_refresh = _create_refresh_token(user, db)
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=raw_refresh)


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
