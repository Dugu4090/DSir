from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.content import Concept, Course
from src.schemas.content import ConceptRead, CourseRead

router = APIRouter()


@router.get("/", response_model=list[CourseRead])
async def list_courses(db: AsyncSession = Depends(get_db)) -> list[Course]:
    result = await db.execute(
        select(Course).where(Course.is_published.is_(True)).order_by(Course.title)
    )
    return list(result.scalars().all())


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: UUID, db: AsyncSession = Depends(get_db)) -> Course:
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.get("/{course_id}/concepts", response_model=list[ConceptRead])
async def list_course_concepts(
    course_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[Concept]:
    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == course_id)
        .order_by(Concept.created_at)
    )
    return list(result.scalars().all())


@router.get("/{course_id}/concepts/{concept_slug}", response_model=ConceptRead)
async def get_concept(
    course_id: UUID, concept_slug: str, db: AsyncSession = Depends(get_db)
) -> Concept:
    result = await db.execute(
        select(Concept).where(
            Concept.course_id == course_id, Concept.slug == concept_slug
        )
    )
    concept = result.scalar_one_or_none()
    if concept is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")
    return concept
