from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.revision import RevisionSchedule

if TYPE_CHECKING:
    pass


class RevisionEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_schedule(self, user_id: UUID, concept_id: UUID) -> RevisionSchedule:
        result = await self.db.execute(
            select(RevisionSchedule).where(
                RevisionSchedule.user_id == user_id,
                RevisionSchedule.concept_id == concept_id,
            )
        )
        schedule = result.scalar_one_or_none()
        if schedule is None:
            schedule = RevisionSchedule(
                user_id=user_id,
                concept_id=concept_id,
                interval_days=1,
                ease_factor=2.5,
                due_at=datetime.now(timezone.utc),
            )
            self.db.add(schedule)
        return schedule

    async def schedule_review(
        self, user_id: UUID, concept_id: UUID, quality: int
    ) -> RevisionSchedule:
        schedule = await self.get_schedule(user_id, concept_id)
        quality = max(0, min(5, quality))

        if quality >= 3:
            if schedule.interval_days == 1:
                schedule.interval_days = 3
            else:
                schedule.interval_days = max(1, int(schedule.interval_days * schedule.ease_factor))
        else:
            schedule.interval_days = 1

        ease_delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        schedule.ease_factor = max(1.3, schedule.ease_factor + ease_delta)
        schedule.last_reviewed_at = datetime.now(timezone.utc)
        schedule.due_at = datetime.now(timezone.utc) + timedelta(days=schedule.interval_days)
        await self.db.flush()
        return schedule

    async def get_due_concepts(self, user_id: UUID, limit: int = 20) -> list[RevisionSchedule]:
        result = await self.db.execute(
            select(RevisionSchedule)
            .where(
                RevisionSchedule.user_id == user_id,
                RevisionSchedule.due_at <= datetime.now(timezone.utc),
            )
            .order_by(RevisionSchedule.due_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def build_revision_queue(self, user_id: UUID, limit: int = 10) -> list[RevisionSchedule]:
        due = await self.get_due_concepts(user_id, limit=limit * 2)
        return due[:limit]
