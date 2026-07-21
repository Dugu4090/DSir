from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.content import Concept
from src.models.learning import ConceptMastery
from src.schemas.mastery import ConceptMasteryRead, StrengthsWeaknesses
from src.services.mastery import MasteryEngine

router = APIRouter()


@router.get("/user/{user_id}", response_model=list[ConceptMasteryRead])
async def list_mastery(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[ConceptMastery]:
    result = await db.execute(
        select(ConceptMastery)
        .where(ConceptMastery.user_id == user_id)
        .order_by(ConceptMastery.score.asc())
    )
    return list(result.scalars().all())


@router.get("/user/{user_id}/concept/{concept_id}", response_model=ConceptMasteryRead)
async def get_concept_mastery(
    user_id: UUID, concept_id: UUID, db: AsyncSession = Depends(get_db)
) -> ConceptMastery:
    engine = MasteryEngine(db)
    mastery = await engine.get_mastery(user_id, concept_id)
    if mastery.score == 0 and mastery.attempts == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No mastery data for this concept"
        )
    return mastery


@router.get("/user/{user_id}/strengths-weaknesses", response_model=StrengthsWeaknesses)
async def get_strengths_weaknesses(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> StrengthsWeaknesses:
    engine = MasteryEngine(db)
    strengths, weaknesses = await engine.get_strengths_and_weaknesses(user_id)
    return StrengthsWeaknesses(
        strengths=list(strengths),
        weaknesses=list(weaknesses),
    )


@router.post("/record", response_model=ConceptMasteryRead)
async def record_attempt(
    user_id: UUID,
    concept_id: UUID,
    is_correct: bool,
    source: str = "exercise",
    difficulty: float = 1.0,
    db: AsyncSession = Depends(get_db),
) -> ConceptMastery:
    result = await db.execute(select(Concept).where(Concept.id == concept_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")

    engine = MasteryEngine(db)
    mastery = await engine.record_attempt(user_id, concept_id, is_correct, difficulty, source)
    # Build response before commit to avoid expired ORM attributes
    response = ConceptMasteryRead.model_validate(mastery)
    await db.commit()
    return response
