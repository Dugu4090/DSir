from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.content import Course, Roadmap, RoadmapCourse
from src.schemas.roadmap import (
    RoadmapCreate,
    RoadmapDetail,
    RoadmapRead,
    RoadmapUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[RoadmapRead])
async def list_roadmaps(db: AsyncSession = Depends(get_db)) -> list[Roadmap]:
    result = await db.execute(
        select(Roadmap).where(Roadmap.is_published.is_(True)).order_by(Roadmap.title)
    )
    return list(result.scalars().all())


@router.get("/{roadmap_id}", response_model=RoadmapDetail)
async def get_roadmap(roadmap_id: UUID, db: AsyncSession = Depends(get_db)) -> Roadmap:
    result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    roadmap = result.scalar_one_or_none()
    if roadmap is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return roadmap


@router.post("/", response_model=RoadmapRead, status_code=status.HTTP_201_CREATED)
async def create_roadmap(data: RoadmapCreate, db: AsyncSession = Depends(get_db)) -> Roadmap:
    existing = await db.execute(select(Roadmap).where(Roadmap.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    roadmap = Roadmap(**data.model_dump())
    db.add(roadmap)
    await db.commit()
    await db.refresh(roadmap)
    return roadmap


@router.put("/{roadmap_id}", response_model=RoadmapRead)
async def update_roadmap(
    roadmap_id: UUID, data: RoadmapUpdate, db: AsyncSession = Depends(get_db)
) -> Roadmap:
    result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    roadmap = result.scalar_one_or_none()
    if roadmap is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(roadmap, field, value)

    await db.commit()
    await db.refresh(roadmap)
    return roadmap


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roadmap(roadmap_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    roadmap = result.scalar_one_or_none()
    if roadmap is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    await db.delete(roadmap)
    await db.commit()


@router.post("/{roadmap_id}/courses", status_code=status.HTTP_201_CREATED)
async def link_course_to_roadmap(
    roadmap_id: UUID, course_id: UUID, position: int = 0, db: AsyncSession = Depends(get_db)
) -> dict:
    roadmap = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    if roadmap.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    course = await db.execute(select(Course).where(Course.id == course_id))
    if course.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = await db.execute(
        select(RoadmapCourse).where(
            RoadmapCourse.roadmap_id == roadmap_id, RoadmapCourse.course_id == course_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course already linked")

    link = RoadmapCourse(roadmap_id=roadmap_id, course_id=course_id, position=position)
    db.add(link)
    await db.commit()
    return {"status": "ok"}


@router.get("/{roadmap_id}/courses", response_model=list[dict])
async def get_roadmap_courses(
    roadmap_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[dict]:
    result = await db.execute(
        select(Course)
        .join(RoadmapCourse, RoadmapCourse.course_id == Course.id)
        .where(RoadmapCourse.roadmap_id == roadmap_id)
        .order_by(RoadmapCourse.position)
    )
    courses = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "slug": c.slug,
            "title": c.title,
            "technology": c.technology,
            "description": c.description,
        }
        for c in courses
    ]
