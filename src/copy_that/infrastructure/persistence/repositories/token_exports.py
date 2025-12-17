from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.token_exports import TokenExport as TokenExportEntity
from copy_that.infrastructure.persistence.models import TokenExport as TokenExportModel


def _to_entity(model: TokenExportModel) -> TokenExportEntity:
    return TokenExportEntity(
        id=model.id,
        library_id=model.library_id,
        format=model.format,
        file_path=model.file_path,
        file_size=model.file_size,
        exported_at=model.exported_at,
    )


class SQLAlchemyTokenExportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        library_id: int,
        format: str,
        file_size: int | None,
        file_path: str | None = None,
    ) -> TokenExportEntity:
        export = TokenExportModel(
            library_id=library_id,
            format=format,
            file_size=file_size,
            file_path=file_path,
        )
        self._session.add(export)
        await self._session.commit()
        await self._session.refresh(export)
        return _to_entity(export)
