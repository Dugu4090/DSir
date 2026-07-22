from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnrollmentCreate(BaseModel):
    roadmap_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None


class EnrollmentRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    roadmap_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    model_config = ConfigDict(from_attributes=True)
