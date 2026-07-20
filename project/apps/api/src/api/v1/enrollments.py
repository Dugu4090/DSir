from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.content import Course, Roadmap
from src.models.learning import Enrollment
from src.models.user import User
from src.schemas.enrollment import EnrollmentCreate, EnrollmentRead

router = APIRouter()


@router.get("/", response_model=list[EnrollmentRead])
async def list_enrollments(user_id: UUID, db: AsyncSession = Depends(get_db)) -> list[Enrollment]:
    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == user_id)
        .order_by(Enrollment.started_at.desc())
    )
    return list(result.scalars().all())


@router.post("/", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    user_id: UUID, data: EnrollmentCreate, db: AsyncSession = Depends(get_db)
) -> Enrollment:
    if data.roadmap_id:
        result = await db.execute(select(Roadmap).where(Roadmap.id == data.roadmap_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    if data.course_id:
        result = await db.execute(select(Course).where(Course.id == data.course_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.roadmap_id == data.roadmap_id,
            Enrollment.course_id == data.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled"
        )

    enrollment = Enrollment(
        user_id=user_id,
        roadmap_id=data.roadmap_id,
        course_id=data.course_id,
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.id == enrollment_id, Enrollment.user_id == user_id
        )
    )
    enrollment = result.scalar_one_or_none()
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    await db.delete(enrollment)
    await db.commit()
