from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user, require_admin
from src.core.security import get_password_hash
from src.db.session import get_db
from src.models.user import User, UserRole
from src.schemas.common import PaginationParams, PaginatedResponse
from src.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    total_result = await db.execute(select(User))
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    users = result.scalars().all()

    return PaginatedResponse(
        items=[UserRead.model_validate(u).model_dump() for u in users],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    existing = await db.execute(select(User).where(User.email == user.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    await db.flush()
    db.add(UserRole(user_id=db_user.id, role="learner"))
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/{user_id}/roles", status_code=status.HTTP_201_CREATED)
async def add_role(
    user_id: UUID,
    role: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = await db.execute(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role == role)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already assigned")

    db.add(UserRole(user_id=user_id, role=role))
    await db.commit()
    return {"status": "ok"}
