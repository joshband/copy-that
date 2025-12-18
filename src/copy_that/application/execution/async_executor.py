from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class AsyncExecutor:
    """Run blocking work in a thread to keep the event loop responsive."""

    async def run(self, func: Callable[..., T], *args, **kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)
