from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.layout_tokens import LayoutToken as LayoutTokenEntity
from copy_that.domain.layout_tokens import LayoutTokenCreate
from copy_that.infrastructure.persistence.models import LayoutToken as LayoutTokenModel


def _to_entity(model: LayoutTokenModel) -> LayoutTokenEntity:
    return LayoutTokenEntity(
        id=model.id,
        project_id=model.project_id,
        extraction_job_id=model.extraction_job_id,
        name=model.name,
        role=model.role,
        value_px=model.value_px,
        value_json=model.value_json,
        confidence=model.confidence,
        created_at=model.created_at,
    )


class SQLAlchemyLayoutTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_extraction(
        self,
        *,
        project_id: int,
        extraction_job_id: int | None,
        tokens: Sequence[LayoutTokenCreate],
    ) -> int:
        count = 0
        for token in tokens:
            self._session.add(
                LayoutTokenModel(
                    project_id=project_id,
                    extraction_job_id=extraction_job_id,
                    name=token.name,
                    role=token.role,
                    value_px=token.value_px,
                    value_json=token.value_json,
                    confidence=token.confidence or 0.0,
                )
            )
            count += 1
        await self._session.commit()
        return count

    async def list_by_project(self, *, project_id: int) -> list[LayoutTokenEntity]:
        result = await self._session.execute(
            select(LayoutTokenModel)
            .where(LayoutTokenModel.project_id == project_id)
            .order_by(LayoutTokenModel.created_at.desc())
        )
        return [_to_entity(t) for t in result.scalars().all()]

    async def list_all(self, *, project_id: int | None) -> list[LayoutTokenEntity]:
        query = select(LayoutTokenModel)
        if project_id is not None:
            query = query.where(LayoutTokenModel.project_id == project_id)
        result = await self._session.execute(query)
        return [_to_entity(t) for t in result.scalars().all()]
