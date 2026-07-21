from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import require_content_creator
from src.db.session import get_db
from src.models.content import Concept, Lesson
from src.models.user import User
from src.schemas.common import PaginationParams, PaginatedResponse
from src.schemas.lesson import LessonDetail, LessonRead

router = APIRouter()


@router.get("/concept/{concept_id}", response_model=PaginatedResponse)
async def list_lessons(
    concept_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    total_result = await db.execute(select(Lesson).where(Lesson.concept_id == concept_id))
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(Lesson)
        .where(Lesson.concept_id == concept_id)
        .order_by(Lesson.position)
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    lessons = result.scalars().all()

    return PaginatedResponse(
        items=[LessonRead.model_validate(l).model_dump() for l in lessons],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson(lesson_id: UUID, db: AsyncSession = Depends(get_db)) -> Lesson:
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson


@router.get("/concept/{concept_id}/next", response_model=LessonRead | None)
async def get_next_lesson(
    concept_id: UUID, current_lesson_id: UUID, db: AsyncSession = Depends(get_db)
) -> Lesson | None:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.concept_id == concept_id, Lesson.id != current_lesson_id)
        .order_by(Lesson.position)
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.post("/", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson: LessonDetail,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Lesson:
    concept = await db.execute(select(Concept).where(Concept.id == lesson.concept_id))
    if concept.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")

    db_lesson = Lesson(**lesson.model_dump(exclude={"id", "created_at"}))
    db.add(db_lesson)
    await db.commit()
    await db.refresh(db_lesson)
    return db_lesson
