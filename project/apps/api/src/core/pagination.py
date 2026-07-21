from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.schemas.common import PaginatedResponse, PaginationParams


async def paginate(
    db: AsyncSession,
    query: Select,
    pagination: PaginationParams,
) -> PaginatedResponse:
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    paginated = query.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    result = await db.execute(paginated)
    items = result.scalars().all()

    return PaginatedResponse(
        items=list(items),
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )
