import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal
from src.models.content import Concept, Course, Roadmap, RoadmapCourse


async def seed_courses(db: AsyncSession) -> None:
    python = Course(
        id=uuid4(),
        slug="python",
        title="Python Fundamentals",
        description="Learn Python from scratch.",
        technology="python",
        is_published=True,
    )
    js = Course(
        id=uuid4(),
        slug="javascript",
        title="JavaScript Fundamentals",
        description="Learn JavaScript from scratch.",
        technology="javascript",
        is_published=True,
    )
    db.add_all([python, js])
    await db.flush()

    variables = Concept(
        id=uuid4(),
        course_id=python.id,
        slug="variables",
        title="Variables",
        description="Store data in variables.",
        prerequisites=[],
    )
    functions = Concept(
        id=uuid4(),
        course_id=python.id,
        slug="functions",
        title="Functions",
        description="Define reusable blocks of code.",
        prerequisites=[variables.id],
    )
    db.add_all([variables, functions])

    roadmap = Roadmap(
        id=uuid4(),
        slug="full-stack-developer",
        title="Full Stack Developer",
        description="Become a full stack developer.",
        is_published=True,
    )
    db.add(roadmap)
    await db.flush()

    db.add_all([
        RoadmapCourse(roadmap_id=roadmap.id, course_id=python.id, position=1),
        RoadmapCourse(roadmap_id=roadmap.id, course_id=js.id, position=2),
    ])


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_courses(db)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
