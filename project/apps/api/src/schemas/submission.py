from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    lesson_id: uuid.UUID | None = None
    concept_id: uuid.UUID | None = None
    submission_type: str
    payload: dict


class SubmissionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    lesson_id: uuid.UUID | None = None
    concept_id: uuid.UUID | None = None
    submission_type: str
    score: int | None = None
    submitted_at: datetime
    evaluated_at: datetime | None = None

    class Config:
        from_attributes = True


class SubmissionDetail(SubmissionRead):
    payload: dict
    evaluation: dict | None = None
