from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class LessonRead(BaseModel):
    id: uuid.UUID
    concept_id: uuid.UUID
    slug: str
    title: str
    lesson_type: str
    position: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LessonDetail(LessonRead):
    content: dict[str, Any]
    meta: dict[str, Any] = {}
