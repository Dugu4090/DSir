import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    technology: str
    is_published: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConceptRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    difficulty: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
