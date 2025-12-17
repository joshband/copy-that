from __future__ import annotations

from typing import Protocol

from copy_that.domain.token_libraries import TokenLibrary


class TokenLibraryRepository(Protocol):
    async def get(self, *, session_id: int, token_type: str) -> TokenLibrary | None: ...

    async def create(
        self,
        *,
        session_id: int,
        token_type: str,
        statistics: str | None,
        name: str | None = None,
    ) -> TokenLibrary: ...

    async def get_or_create(
        self,
        *,
        session_id: int,
        token_type: str,
        statistics: str | None,
    ) -> TokenLibrary: ...

    async def mark_curated(self, *, library_id: int, notes: str | None) -> TokenLibrary | None: ...
