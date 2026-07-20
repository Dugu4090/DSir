from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ProjectRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectDetail(ProjectRead):
    requirements: dict = {}
    starter_files: dict = {}
    meta: dict = {}


class ProjectSubmissionCreate(BaseModel):
    project_id: uuid.UUID
    repository_url: str | None = None
    files: dict | None = None


class ProjectSubmissionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    project_id: uuid.UUID
    repository_url: str | None = None
    score: int | None = None
    submitted_at: datetime
    reviewed_at: datetime | None = None

    class Config:
        from_attributes = True


class ProjectSubmissionDetail(ProjectSubmissionRead):
    files: dict | None = None
    feedback: dict | None = None
