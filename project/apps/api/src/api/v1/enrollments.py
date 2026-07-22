from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.content import Course, Roadmap
from src.models.learning import Enrollment
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.enrollment import EnrollmentCreate, EnrollmentRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_enrollments(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(Enrollment).where(Enrollment.user_id == current_user.id)
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(Enrollment.started_at.desc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    enrollments = result.scalars().all()

    return PaginatedResponse(
        items=[EnrollmentRead.model_validate(e).model_dump() for e in enrollments],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.post("/", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    data: EnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
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
            Enrollment.user_id == current_user.id,
            Enrollment.roadmap_id == data.roadmap_id,
            Enrollment.course_id == data.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled")

    enrollment = Enrollment(
        user_id=current_user.id,
        roadmap_id=data.roadmap_id,
        course_id=data.course_id,
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id, Enrollment.user_id == current_user.id)
    )
    enrollment = result.scalar_one_or_none()
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    await db.delete(enrollment)
    await db.commit()
