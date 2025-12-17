from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.token_libraries import TokenLibrary as TokenLibraryEntity
from copy_that.infrastructure.persistence.models import TokenLibrary as TokenLibraryModel


def _to_entity(model: TokenLibraryModel) -> TokenLibraryEntity:
    return TokenLibraryEntity(
        id=model.id,
        session_id=model.session_id,
        token_type=model.token_type,
        name=model.name,
        statistics=model.statistics,
        is_curated=model.is_curated,
        curation_notes=model.curation_notes,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyTokenLibraryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, *, session_id: int, token_type: str) -> TokenLibraryEntity | None:
        result = await self._session.execute(
            select(TokenLibraryModel)
            .where(TokenLibraryModel.session_id == session_id)
            .where(TokenLibraryModel.token_type == token_type)
        )
        library = result.scalar_one_or_none()
        return _to_entity(library) if library else None

    async def create(
        self,
        *,
        session_id: int,
        token_type: str,
        statistics: str | None,
        name: str | None = None,
    ) -> TokenLibraryEntity:
        library = TokenLibraryModel(
            session_id=session_id,
            token_type=token_type,
            statistics=statistics,
            name=name,
        )
        self._session.add(library)
        await self._session.commit()
        await self._session.refresh(library)
        return _to_entity(library)

    async def get_or_create(
        self,
        *,
        session_id: int,
        token_type: str,
        statistics: str | None,
    ) -> TokenLibraryEntity:
        existing = await self.get(session_id=session_id, token_type=token_type)
        if existing:
            if statistics is not None:
                result = await self._session.execute(
                    select(TokenLibraryModel).where(TokenLibraryModel.id == existing.id)
                )
                model = result.scalar_one()
                model.statistics = statistics
                self._session.add(model)
                await self._session.commit()
                await self._session.refresh(model)
                return _to_entity(model)
            return existing
        return await self.create(
            session_id=session_id, token_type=token_type, statistics=statistics, name=None
        )

    async def mark_curated(
        self, *, library_id: int, notes: str | None
    ) -> TokenLibraryEntity | None:
        result = await self._session.execute(
            select(TokenLibraryModel).where(TokenLibraryModel.id == library_id)
        )
        library = result.scalar_one_or_none()
        if not library:
            return None
        library.is_curated = True
        library.curation_notes = notes
        self._session.add(library)
        await self._session.commit()
        await self._session.refresh(library)
        return _to_entity(library)
