from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ConceptMasteryRead(BaseModel):
    concept_id: uuid.UUID
    score: int
    confidence: int
    attempts: int
    correct_streak: int
    last_reviewed_at: datetime | None = None
    next_review_at: datetime | None = None
    updated_at: datetime

    class Config:
        from_attributes = True


class StrengthsWeaknesses(BaseModel):
    strengths: list[ConceptMasteryRead]
    weaknesses: list[ConceptMasteryRead]
