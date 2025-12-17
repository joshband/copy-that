from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.spacing_tokens import SpacingToken as SpacingTokenEntity
from copy_that.domain.spacing_tokens import SpacingTokenCreate
from copy_that.infrastructure.persistence.models import ExtractionJob
from copy_that.infrastructure.persistence.models import SpacingToken as SpacingTokenModel


def _to_entity(model: SpacingTokenModel) -> SpacingTokenEntity:
    return SpacingTokenEntity(
        id=model.id,
        project_id=model.project_id,
        extraction_job_id=model.extraction_job_id,
        value_px=model.value_px,
        name=model.name,
        semantic_role=model.semantic_role,
        spacing_type=model.spacing_type,
        category=model.category,
        confidence=model.confidence,
        usage=model.usage,
        created_at=model.created_at,
    )


class SQLAlchemySpacingTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        tokens: Sequence[SpacingTokenCreate],
        result_data: dict[str, object],
    ) -> int:
        job = ExtractionJob(
            project_id=project_id,
            source_url=source_url,
            extraction_type="spacing",
            status="completed",
            result_data=json.dumps(result_data, default=str),
        )
        self._session.add(job)
        await self._session.flush()

        for token in tokens:
            self._session.add(
                SpacingTokenModel(
                    project_id=project_id,
                    extraction_job_id=job.id,
                    value_px=token.value_px,
                    name=token.name,
                    semantic_role=token.semantic_role,
                    spacing_type=token.spacing_type,
                    category=token.category,
                    confidence=token.confidence or 0.0,
                    usage=token.usage,
                )
            )

        await self._session.commit()
        return int(job.id)

    async def list_by_project(self, *, project_id: int) -> list[SpacingTokenEntity]:
        result = await self._session.execute(
            select(SpacingTokenModel)
            .where(SpacingTokenModel.project_id == project_id)
            .order_by(SpacingTokenModel.created_at.desc())
        )
        return [_to_entity(t) for t in result.scalars().all()]

    async def list_all(self, *, project_id: int | None) -> list[SpacingTokenEntity]:
        query = select(SpacingTokenModel)
        if project_id is not None:
            query = query.where(SpacingTokenModel.project_id == project_id)
        result = await self._session.execute(query)
        return [_to_entity(t) for t in result.scalars().all()]
