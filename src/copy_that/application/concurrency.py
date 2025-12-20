from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

_max_concurrency = int(os.getenv("EXTRACTION_MAX_CONCURRENCY", "4"))
_semaphore = asyncio.Semaphore(_max_concurrency)


@asynccontextmanager
async def extract_slot():
    """Limit concurrent extraction to avoid OOM."""
    async with _semaphore:
        yield
