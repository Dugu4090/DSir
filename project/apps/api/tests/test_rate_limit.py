from __future__ import annotations

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient

from src.core.rate_limit import RateLimiter, _MemoryStore


@pytest.mark.asyncio
async def test_memory_store_cleans_empty_keys() -> None:
    store = _MemoryStore()
    # Increment to create a key
    await store.increment("key-a", window=60, limit=10)
    assert "key-a" in store._data
    # Wait for the entry to expire, then increment again and verify cleanup
    import time

    await store.increment("key-a", window=0, limit=10)
    assert "key-a" not in store._data


@pytest.mark.asyncio
async def test_memory_store_enforces_limit() -> None:
    store = _MemoryStore()
    limit = 2
    for i in range(limit):
        count = await store.increment("key-b", window=60, limit=limit)
        assert count <= limit

    with pytest.raises(Exception) as exc_info:
        await store.increment("key-b", window=60, limit=limit)
    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS  # type: ignore[attr-defined]


def test_rate_limiter_dependency_rejects_excess_requests() -> None:
    from src.core.config import settings

    # Tests disable rate limiting globally; opt-in for this test.
    settings.RATE_LIMIT_ENABLED = True
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(
        request: Request,
        _rate_limit: None = RateLimiter("2/minute"),
    ) -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)
    assert client.get("/test").status_code == 200
    assert client.get("/test").status_code == 200
    response = client.get("/test")
    settings.RATE_LIMIT_ENABLED = False
    assert response.status_code == 429
