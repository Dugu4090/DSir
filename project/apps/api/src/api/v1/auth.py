from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.config import settings
from src.core.security import create_access_token, get_password_hash, verify_password
from src.db.session import get_db
from src.models.user import RefreshToken, User
from src.schemas.auth import LoginRequest, RegisterRequest, TokenPair
from src.schemas.user import UserRead

router = APIRouter()


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
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=str(uuid4()),
        expires_at=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    db.add(refresh_token)
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=refresh_token.token_hash)


@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=str(uuid4()),
        expires_at=datetime.now(timezone.utc) + settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    db.add(refresh_token)
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=refresh_token.token_hash)


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
