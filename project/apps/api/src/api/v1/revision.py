from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.revision import RevisionSchedule, RevisionSession
from src.models.user import User
from src.schemas.common import PaginationParams, PaginatedResponse
from src.schemas.revision import (
    ReviewRequest,
    ReviewResponse,
    RevisionScheduleRead,
    RevisionSessionRead,
    RevisionSessionStart,
)
from src.services.revision import RevisionEngine

router = APIRouter()


@router.get("/due", response_model=list[RevisionScheduleRead])
async def get_due_revisions(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[RevisionSchedule]:
    engine = RevisionEngine(db)
    return await engine.build_revision_queue(current_user.id, limit=limit)


@router.get("/schedule/{concept_id}", response_model=RevisionScheduleRead)
async def get_schedule(
    concept_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RevisionSchedule:
    engine = RevisionEngine(db)
    schedule = await engine.get_schedule(current_user.id, concept_id)
    return schedule


@router.post("/review", response_model=ReviewResponse)
async def submit_review(
    data: ReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    engine = RevisionEngine(db)
    schedule = await engine.schedule_review(current_user.id, data.concept_id, data.quality)

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
    data: RevisionSessionStart,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RevisionSession:
    session = RevisionSession(
        user_id=current_user.id,
        concepts=data.concept_ids or [],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.put("/sessions/{session_id}/complete", response_model=RevisionSessionRead)
async def complete_revision_session(
    session_id: UUID,
    results: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RevisionSession:
    result = await db.execute(
        select(RevisionSession).where(RevisionSession.id == session_id)
    )
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


@router.get("/sessions", response_model=PaginatedResponse)
async def list_revision_sessions(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    from src.core.pagination import paginated_response
    from src.schemas.revision import RevisionSessionRead

    query = select(RevisionSession).where(RevisionSession.user_id == current_user.id)
    return await paginated_response(db, query, pagination, RevisionSessionRead)
