from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment import Project
from src.models.content import Concept, Course, Lesson, Roadmap
from src.models.user import User


async def test_list_roadmaps(client: TestClient, db_session: AsyncSession):
    db_session.add(
        Roadmap(
            id=uuid4(),
            slug="test-roadmap",
            title="Test Roadmap",
            is_published=True,
        )
    )
    db_session.add(
        Roadmap(
            id=uuid4(),
            slug="unpublished",
            title="Unpublished",
            is_published=False,
        )
    )
    await db_session.flush()

    response = client.get("/api/v1/roadmaps/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "test-roadmap"


def test_get_roadmap_not_found(client: TestClient):
    response = client.get(f"/api/v1/roadmaps/{uuid4()}")
    assert response.status_code == 404


async def test_list_courses(client: TestClient, db_session: AsyncSession):
    db_session.add(
        Course(
            id=uuid4(),
            slug="python",
            title="Python",
            technology="python",
            is_published=True,
        )
    )
    await db_session.flush()

    response = client.get("/api/v1/courses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


async def test_get_course(client: TestClient, db_session: AsyncSession):
    course_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            is_published=True,
        )
    )
    await db_session.flush()

    response = client.get(f"/api/v1/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["slug"] == "python"


async def test_list_course_concepts(client: TestClient, db_session: AsyncSession):
    course_id = uuid4()
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    await db_session.flush()

    db_session.add(
        Concept(course_id=course_id, slug="variables", title="Variables")
    )
    await db_session.flush()

    response = client.get(f"/api/v1/courses/{course_id}/concepts")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_concept_by_slug(client: TestClient, db_session: AsyncSession):
    course_id = uuid4()
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    await db_session.flush()

    db_session.add(
        Concept(course_id=course_id, slug="variables", title="Variables")
    )
    await db_session.flush()

    response = client.get(f"/api/v1/courses/{course_id}/concepts/variables")
    assert response.status_code == 200
    assert response.json()["slug"] == "variables"


async def test_create_enrollment(client: TestClient, db_session: AsyncSession):
    user_id = uuid4()
    course_id = uuid4()
    db_session.add(User(id=user_id, email="test@example.com", hashed_password="secret"))
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    await db_session.flush()

    response = client.post(
        f"/api/v1/enrollments/?user_id={user_id}",
        json={"course_id": str(course_id), "roadmap_id": None},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "active"


async def test_create_submission(client: TestClient, db_session: AsyncSession):
    user_id = uuid4()
    db_session.add(User(id=user_id, email="test@example.com", hashed_password="secret"))
    await db_session.flush()

    response = client.post(
        f"/api/v1/submissions/?user_id={user_id}",
        json={
            "submission_type": "code",
            "payload": {"code": "print('hello')"},
            "lesson_id": None,
            "concept_id": None,
        },
    )
    assert response.status_code == 201
    assert response.json()["submission_type"] == "code"


async def test_record_mastery(client: TestClient, db_session: AsyncSession):
    user_id = uuid4()
    course_id = uuid4()
    concept_id = uuid4()
    db_session.add(User(id=user_id, email="test@example.com", hashed_password="secret"))
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    await db_session.flush()

    response = client.post(
        f"/api/v1/mastery/record?user_id={user_id}&concept_id={concept_id}&is_correct=true"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] > 0
    assert data["attempts"] == 1


async def test_revision_submit_review(client: TestClient, db_session: AsyncSession):
    user_id = uuid4()
    course_id = uuid4()
    concept_id = uuid4()
    db_session.add(User(id=user_id, email="test@example.com", hashed_password="secret"))
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    await db_session.flush()

    response = client.post(
        f"/api/v1/revision/review?user_id={user_id}",
        json={"concept_id": str(concept_id), "quality": 4},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["new_interval_days"] > 0


def test_ai_chat(client: TestClient):
    response = client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Hello"}], "mode": "mentor"},
    )
    assert response.status_code == 200
    assert "mock" in response.json()["content"].lower()


def test_ai_code_review(client: TestClient):
    response = client.post(
        "/api/v1/ai/code-review",
        json={"code": "print('hello')", "language": "python"},
    )
    assert response.status_code == 200
    assert response.json()["feedback"]


def test_execute_code(client: TestClient):
    response = client.post(
        "/api/v1/execution/run",
        json={"code": "print('hello')", "language": "python"},
    )
    assert response.status_code == 200
    assert response.json()["exit_code"] == 0


def test_get_profile_not_found(client: TestClient):
    response = client.get(f"/api/v1/profiles/{uuid4()}")
    assert response.status_code == 404


async def test_list_lessons(client: TestClient, db_session: AsyncSession):
    course_id = uuid4()
    concept_id = uuid4()
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    db_session.add(
        Lesson(
            id=uuid4(),
            concept_id=concept_id,
            slug="intro",
            title="Introduction",
            content={"text": "Hello"},
            position=1,
        )
    )
    await db_session.flush()

    response = client.get(f"/api/v1/lessons/concept/{concept_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_lesson(client: TestClient, db_session: AsyncSession):
    lesson_id = uuid4()
    concept_id = uuid4()
    course_id = uuid4()
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    db_session.add(
        Lesson(
            id=lesson_id,
            concept_id=concept_id,
            slug="intro",
            title="Introduction",
            content={"text": "Hello"},
            position=1,
        )
    )
    await db_session.flush()

    response = client.get(f"/api/v1/lessons/{lesson_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Introduction"


def test_create_roadmap(client: TestClient):
    response = client.post(
        "/api/v1/roadmaps/",
        json={"slug": "new-roadmap", "title": "New Roadmap", "is_published": False},
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "new-roadmap"


async def test_list_projects(client: TestClient, db_session: AsyncSession):
    course_id = uuid4()
    db_session.add(
        Course(id=course_id, slug="python", title="Python", technology="python", is_published=True)
    )
    db_session.add(
        Project(
            id=uuid4(),
            course_id=course_id,
            slug="calculator",
            title="Calculator App",
        )
    )
    await db_session.flush()

    response = client.get(f"/api/v1/projects/course/{course_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
