from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.user import User, UserProfile
from src.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter()


@router.get("/{user_id}", response_model=ProfileRead)
async def get_profile(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/{user_id}", response_model=ProfileRead)
async def update_profile(
    user_id: UUID, data: ProfileUpdate, db: AsyncSession = Depends(get_db)
) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()

    if profile is None:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile
