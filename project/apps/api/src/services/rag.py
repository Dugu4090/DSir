from __future__ import annotations

import os
import random
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.session import AsyncSessionLocal
from src.models.knowledge import KnowledgeChunk
from src.models.learning import ConceptMastery


class EmbeddingProvider:
    """Generate vector embeddings for text."""

    def __init__(self, dimensions: int = 1536, api_key: str | None = None):
        self.dimensions = dimensions
        self.api_key = api_key or settings.OPENAI_API_KEY

    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector for the given text."""
        if self.api_key:
            return await self._openai_embed(text)
        return self._mock_embed(text)

    async def _openai_embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"input": text, "model": "text-embedding-3-small"},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return list(data["data"][0]["embedding"])

    def _mock_embed(self, text: str) -> list[float]:
        """Deterministic mock embedding for testing and local development."""
        random.seed(text)
        return [random.uniform(-1, 1) for _ in range(self.dimensions)]  # noqa: S311


class RAGService:
    """Service for semantic search over knowledge chunks."""

    def __init__(self, db: AsyncSession, embedding_provider: EmbeddingProvider | None = None):
        self.db = db
        self.embedding_provider = embedding_provider or EmbeddingProvider()

    async def index_chunk(
        self,
        content: str,
        chunk_type: str = "lesson",
        course_id: UUID | None = None,
        concept_id: UUID | None = None,
        meta: dict | None = None,
    ) -> KnowledgeChunk:
        """Index a knowledge chunk with an embedding."""
        embedding = await self.embedding_provider.embed(content)
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
        embedding = await self.embedding_provider.embed(query)
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


def get_rag_service() -> RAGService:
    """Factory for RAGService using the async session factory."""
    # Synchronous factory; the caller is responsible for providing a session.
    return RAGService(AsyncSessionLocal())
