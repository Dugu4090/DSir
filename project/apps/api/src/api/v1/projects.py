from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.assessment import Project, ProjectSubmission
from src.models.content import Course
from src.schemas.project import (
    ProjectDetail,
    ProjectRead,
    ProjectSubmissionCreate,
    ProjectSubmissionDetail,
    ProjectSubmissionRead,
)

router = APIRouter()


@router.get("/course/{course_id}", response_model=list[ProjectRead])
async def list_course_projects(
    course_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[Project]:
    result = await db.execute(
        select(Project)
        .where(Project.course_id == course_id)
        .order_by(Project.created_at)
    )
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/submissions", response_model=ProjectSubmissionRead, status_code=status.HTTP_201_CREATED)
async def submit_project(
    user_id: UUID, data: ProjectSubmissionCreate, db: AsyncSession = Depends(get_db)
) -> ProjectSubmission:
    result = await db.execute(select(Project).where(Project.id == data.project_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    submission = ProjectSubmission(
        user_id=user_id,
        project_id=data.project_id,
        repository_url=data.repository_url,
        files=data.files,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/submissions/{submission_id}", response_model=ProjectSubmissionDetail)
async def get_submission(
    submission_id: UUID, db: AsyncSession = Depends(get_db)
) -> ProjectSubmission:
    result = await db.execute(
        select(ProjectSubmission).where(ProjectSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )
    return submission


@router.get("/user/{user_id}/submissions", response_model=list[ProjectSubmissionRead])
async def list_user_submissions(
    user_id: UUID, limit: int = 20, db: AsyncSession = Depends(get_db)
) -> list[ProjectSubmission]:
    result = await db.execute(
        select(ProjectSubmission)
        .where(ProjectSubmission.user_id == user_id)
        .order_by(ProjectSubmission.submitted_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
