from __future__ import annotations

from typing import Protocol

from copy_that.domain.token_exports import TokenExport


class TokenExportRepository(Protocol):
    async def create(
        self,
        *,
        library_id: int,
        format: str,
        file_size: int | None,
        file_path: str | None = None,
    ) -> TokenExport: ...
