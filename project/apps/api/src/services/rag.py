from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import AIManager, get_ai_manager
from src.db.session import AsyncSessionLocal
from src.models.knowledge import KnowledgeChunk
from src.models.learning import ConceptMastery


class RAGService:
    """Service for semantic search over knowledge chunks."""

    def __init__(self, db: AsyncSession, ai: AIManager | None = None):
        self.db = db
        self.ai = ai or get_ai_manager()

    async def index_chunk(
        self,
        content: str,
        chunk_type: str = "lesson",
        course_id: UUID | None = None,
        concept_id: UUID | None = None,
        meta: dict | None = None,
    ) -> KnowledgeChunk:
        """Index a knowledge chunk with an embedding."""
        embedding = await self.ai.embed(content)
        chunk = KnowledgeChunk(
            course_id=course_id,
            concept_id=concept_id,
            chunk_type=chunk_type,
            content=content,
            embedding=embedding,
            meta=meta or {},
        )
        self.db.add(chunk)
        await self.db.flush()
        return chunk

    async def search(
        self,
        query: str,
        limit: int = 5,
        course_id: UUID | None = None,
        concept_id: UUID | None = None,
    ) -> list[KnowledgeChunk]:
        """Semantic search over knowledge chunks."""
        embedding = await self.ai.embed(query)
        dialect = self.db.bind.dialect.name if self.db.bind else "postgresql"

        if dialect == "postgresql":
            from pgvector.sqlalchemy import L2Distance

            stmt = select(KnowledgeChunk).order_by(L2Distance(KnowledgeChunk.embedding, embedding))
        else:
            # Fallback for non-PostgreSQL dialects: return recent chunks
            stmt = select(KnowledgeChunk).order_by(KnowledgeChunk.created_at.desc())

        if course_id is not None:
            stmt = stmt.where(KnowledgeChunk.course_id == course_id)
        if concept_id is not None:
            stmt = stmt.where(KnowledgeChunk.concept_id == concept_id)

        stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search_for_user(self, user_id: UUID, query: str, limit: int = 5) -> list[KnowledgeChunk]:
        """Semantic search scoped to a learner's weak concepts."""
        result = await self.db.execute(
            select(ConceptMastery.concept_id).where(
                ConceptMastery.user_id == user_id,
                ConceptMastery.score < 70,
            )
        )
        concept_ids = [row[0] for row in result.all()]

        if not concept_ids:
            return await self.search(query, limit=limit)

        # Limit to weak concepts; if too few, also search broadly
        chunks: list[KnowledgeChunk] = []
        for concept_id in concept_ids[:limit]:
            chunks.extend(await self.search(query, limit=1, concept_id=concept_id))
        return chunks[:limit]

    async def course_knowledge(self, course_id: UUID, query: str, limit: int = 5) -> list[KnowledgeChunk]:
        """Retrieve relevant knowledge chunks for a course."""
        return await self.search(query, limit=limit, course_id=course_id)


async def get_rag_service() -> RAGService:
    """Factory for RAGService using a fresh async session."""
    async with AsyncSessionLocal() as db:
        return RAGService(db, get_ai_manager())
