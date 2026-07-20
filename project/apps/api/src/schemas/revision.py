from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class RevisionScheduleRead(BaseModel):
    concept_id: uuid.UUID
    interval_days: int
    ease_factor: float
    repetitions: int
    due_at: datetime
    last_reviewed_at: datetime | None = None

    class Config:
        from_attributes = True


class RevisionSessionStart(BaseModel):
    concept_ids: list[uuid.UUID] | None = None


class RevisionSessionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    concepts: list[uuid.UUID]
    results: dict

    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    concept_id: uuid.UUID
    quality: int  # 0-5


class ReviewResponse(BaseModel):
    concept_id: uuid.UUID
    quality: int
    new_interval_days: int
    new_ease_factor: float
    due_at: datetime
