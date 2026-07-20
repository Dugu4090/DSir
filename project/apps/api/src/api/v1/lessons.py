from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.content import Concept, Lesson
from src.schemas.lesson import LessonDetail, LessonRead

router = APIRouter()


@router.get("/concept/{concept_id}", response_model=list[LessonRead])
async def list_lessons(
    concept_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[Lesson]:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.concept_id == concept_id)
        .order_by(Lesson.position)
    )
    return list(result.scalars().all())


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
