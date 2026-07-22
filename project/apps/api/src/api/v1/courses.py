from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import require_content_creator
from src.db.session import get_db
from src.models.content import Concept, Course
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.content import ConceptRead, CourseRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_courses(
    technology: str | None = None,
    published_only: bool = True,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(Course)
    if published_only:
        query = query.where(Course.is_published.is_(True))
    if technology:
        query = query.where(Course.technology == technology)

    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(Course.title).offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    )
    courses = result.scalars().all()

    return PaginatedResponse(
        items=[CourseRead.model_validate(c).model_dump() for c in courses],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: UUID, db: AsyncSession = Depends(get_db)) -> Course:
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseRead,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Course:
    existing = await db.execute(select(Course).where(Course.slug == course.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    db_course = Course(**course.model_dump(exclude={"id", "created_at"}))
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


@router.get("/{course_id}/concepts", response_model=PaginatedResponse)
async def list_course_concepts(
    course_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    total_result = await db.execute(select(Concept).where(Concept.course_id == course_id))
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == course_id)
        .order_by(Concept.created_at)
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    concepts = result.scalars().all()

    return PaginatedResponse(
        items=[ConceptRead.model_validate(c).model_dump() for c in concepts],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/{course_id}/concepts/{concept_slug}", response_model=ConceptRead)
async def get_concept(course_id: UUID, concept_slug: str, db: AsyncSession = Depends(get_db)) -> Concept:
    result = await db.execute(select(Concept).where(Concept.course_id == course_id, Concept.slug == concept_slug))
    concept = result.scalar_one_or_none()
    if concept is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")
    return concept
