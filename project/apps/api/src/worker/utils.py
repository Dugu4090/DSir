from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine from a synchronous Celery task.

    Uses asyncio.run by default. If an loop is already running (e.g. during
    tests), it runs the coroutine on that loop.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    if loop.is_running():
        return loop.run_until_complete(coro)
    return asyncio.run(coro)


def async_to_sync(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """Decorator that wraps an async function so it can be called as sync."""

    def wrapper(*args: Any, **kwargs: Any) -> T:
        return run_async(func(*args, **kwargs))

    return wrapper
