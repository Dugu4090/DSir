from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.content import Course
from src.schemas.content import CourseRead

router = APIRouter()


@router.get("/", response_model=list[CourseRead])
async def list_courses(db: AsyncSession = Depends(get_db)) -> list[Course]:
    result = await db.execute(select(Course).where(Course.is_published.is_(True)))
    return list(result.scalars().all())
