from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class LessonRead(BaseModel):
    id: uuid.UUID
    concept_id: uuid.UUID
    slug: str
    title: str
    lesson_type: str
    position: int
    created_at: datetime

    class Config:
        from_attributes = True


class LessonDetail(LessonRead):
    content: dict
    meta: dict = {}
