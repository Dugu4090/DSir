from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.learning import ConceptMastery

if TYPE_CHECKING:
    pass


class MasteryEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_mastery(self, user_id: UUID, concept_id: UUID) -> ConceptMastery:
        result = await self.db.execute(
            select(ConceptMastery).where(
                ConceptMastery.user_id == user_id,
                ConceptMastery.concept_id == concept_id,
            )
        )
        mastery = result.scalar_one_or_none()
        if mastery is None:
            mastery = ConceptMastery(user_id=user_id, concept_id=concept_id)
            self.db.add(mastery)
        return mastery

    async def record_attempt(
        self,
        user_id: UUID,
        concept_id: UUID,
        is_correct: bool,
        difficulty: float = 1.0,
        source: str = "exercise",
    ) -> ConceptMastery:
        mastery = await self.get_mastery(user_id, concept_id)
        mastery.attempts += 1
        if is_correct:
            mastery.correct_streak += 1
            gain = self._calculate_gain(mastery, difficulty)
            mastery.score = min(100, mastery.score + gain)
            mastery.confidence = min(100, mastery.confidence + 5)
        else:
            mastery.correct_streak = 0
            penalty = self._calculate_penalty(mastery)
            mastery.score = max(0, mastery.score - penalty)
            mastery.confidence = max(0, mastery.confidence - 10)

        mastery.last_reviewed_at = datetime.now(timezone.utc)
        mastery.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return mastery

    def _calculate_gain(self, mastery: ConceptMastery, difficulty: float) -> int:
        base_gain = int(10 * difficulty)
        streak_bonus = min(mastery.correct_streak * 2, 20)
        diminishing = max(0, (100 - mastery.score) // 10)
        return min(base_gain + streak_bonus, base_gain + diminishing)

    def _calculate_penalty(self, mastery: ConceptMastery) -> int:
        confidence_factor = 1 + (mastery.confidence / 100)
        return int(10 * confidence_factor)

    async def apply_decay(self, user_id: UUID, concept_id: UUID) -> ConceptMastery:
        mastery = await self.get_mastery(user_id, concept_id)
        if mastery.last_reviewed_at is None:
            return mastery

        days_since_review = (datetime.now(timezone.utc) - mastery.last_reviewed_at).days
        if days_since_review <= 0:
            return mastery

        lambda_decay = 0.05
        decay_factor = math.exp(-lambda_decay * days_since_review)
        confidence_decay = math.exp(-lambda_decay * days_since_review * 0.5)

        mastery.score = int(mastery.score * decay_factor)
        mastery.confidence = int(mastery.confidence * confidence_decay)
        mastery.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return mastery

    async def get_strengths_and_weaknesses(
        self, user_id: UUID
    ) -> tuple[list[ConceptMastery], list[ConceptMastery]]:
        result = await self.db.execute(
            select(ConceptMastery).where(ConceptMastery.user_id == user_id)
        )
        masteries = list(result.scalars().all())
        strengths = [m for m in masteries if m.score >= 80 and m.confidence >= 70]
        weaknesses = [m for m in masteries if m.score < 50 or m.confidence < 40]
        return strengths, weaknesses
