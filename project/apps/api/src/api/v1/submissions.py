from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.assessment import Submission
from src.models.content import Concept, Lesson
from src.models.user import User
from src.schemas.submission import SubmissionCreate, SubmissionDetail, SubmissionRead

router = APIRouter()


@router.post("/", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
async def create_submission(
    user_id: UUID,
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
) -> Submission:
    if data.lesson_id:
        result = await db.execute(select(Lesson).where(Lesson.id == data.lesson_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    if data.concept_id:
        result = await db.execute(select(Concept).where(Concept.id == data.concept_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")

    submission = Submission(
        user_id=user_id,
        lesson_id=data.lesson_id,
        concept_id=data.concept_id,
        submission_type=data.submission_type,
        payload=data.payload,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/{submission_id}", response_model=SubmissionDetail)
async def get_submission(
    submission_id: UUID, db: AsyncSession = Depends(get_db)
) -> Submission:
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )
    return submission


@router.get("/user/{user_id}", response_model=list[SubmissionRead])
async def list_user_submissions(
    user_id: UUID,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[Submission]:
    result = await db.execute(
        select(Submission)
        .where(Submission.user_id == user_id)
        .order_by(Submission.submitted_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
