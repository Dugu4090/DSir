from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.revision import RevisionProblemQueue, RevisionSchedule, RevisionSession
from src.schemas.revision import (
    ReviewRequest,
    ReviewResponse,
    RevisionScheduleRead,
    RevisionSessionRead,
    RevisionSessionStart,
)
from src.services.revision import RevisionEngine

router = APIRouter()


@router.get("/user/{user_id}/due", response_model=list[RevisionScheduleRead])
async def get_due_revisions(
    user_id: UUID, limit: int = 10, db: AsyncSession = Depends(get_db)
) -> list[RevisionSchedule]:
    engine = RevisionEngine(db)
    return await engine.build_revision_queue(user_id, limit=limit)


@router.get("/user/{user_id}/schedule/{concept_id}", response_model=RevisionScheduleRead)
async def get_schedule(
    user_id: UUID, concept_id: UUID, db: AsyncSession = Depends(get_db)
) -> RevisionSchedule:
    engine = RevisionEngine(db)
    schedule = await engine.get_schedule(user_id, concept_id)
    return schedule


@router.post("/review", response_model=ReviewResponse)
async def submit_review(
    user_id: UUID, data: ReviewRequest, db: AsyncSession = Depends(get_db)
) -> ReviewResponse:
    engine = RevisionEngine(db)
    schedule = await engine.schedule_review(user_id, data.concept_id, data.quality)

    # Build response before commit to avoid expired ORM objects
    response = ReviewResponse(
        concept_id=data.concept_id,
        quality=data.quality,
        new_interval_days=schedule.interval_days,
        new_ease_factor=schedule.ease_factor,
        due_at=schedule.due_at,
    )
    await db.commit()
    return response


@router.post("/sessions", response_model=RevisionSessionRead, status_code=status.HTTP_201_CREATED)
async def start_revision_session(
    user_id: UUID, data: RevisionSessionStart, db: AsyncSession = Depends(get_db)
) -> RevisionSession:
    session = RevisionSession(
        user_id=user_id,
        concepts=data.concept_ids or [],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.put("/sessions/{session_id}/complete", response_model=RevisionSessionRead)
async def complete_revision_session(
    session_id: UUID, results: dict, db: AsyncSession = Depends(get_db)
) -> RevisionSession:
    result = await db.execute(select(RevisionSession).where(RevisionSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    from datetime import UTC, datetime

    session.completed_at = datetime.now(UTC)
    session.results = results
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/user/{user_id}/sessions", response_model=list[RevisionSessionRead])
async def list_revision_sessions(
    user_id: UUID, limit: int = 20, db: AsyncSession = Depends(get_db)
) -> list[RevisionSession]:
    result = await db.execute(
        select(RevisionSession)
        .where(RevisionSession.user_id == user_id)
        .order_by(RevisionSession.started_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
