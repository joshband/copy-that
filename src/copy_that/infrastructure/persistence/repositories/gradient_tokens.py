from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.gradient_tokens import GradientToken as GradientTokenEntity
from copy_that.domain.gradient_tokens import GradientTokenCreate
from copy_that.infrastructure.persistence.models import ExtractionJob
from copy_that.infrastructure.persistence.models import GradientToken as GradientTokenModel


def _to_entity(model: GradientTokenModel) -> GradientTokenEntity:
    return GradientTokenEntity(
        id=model.id,
        project_id=model.project_id,
        extraction_job_id=model.extraction_job_id,
        name=model.name,
        gradient_type=model.gradient_type,
        angle=model.angle,
        stops_json=model.stops_json,
        source=model.source,
        confidence=model.confidence,
        axis=model.axis,
        confirmed_by=model.confirmed_by,
        extraction_metadata=model.extraction_metadata,
        created_at=model.created_at,
    )


class SQLAlchemyGradientTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        gradients: Sequence[GradientTokenCreate],
    ) -> int:
        job = ExtractionJob(
            project_id=project_id,
            source_url=source_url,
            extraction_type="gradient",
            status="completed",
            result_data=json.dumps({"token_count": len(gradients)}),
        )
        self._session.add(job)
        await self._session.flush()

        for gradient in gradients:
            self._session.add(
                GradientTokenModel(
                    project_id=project_id,
                    extraction_job_id=job.id,
                    name=gradient.name,
                    gradient_type=gradient.gradient_type,
                    angle=gradient.angle,
                    stops_json=gradient.stops_json,
                    source=gradient.source,
                    confidence=gradient.confidence,
                    axis=gradient.axis,
                    confirmed_by=gradient.confirmed_by,
                    extraction_metadata=gradient.extraction_metadata,
                )
            )

        await self._session.commit()
        return int(job.id)

    async def list_by_project(self, *, project_id: int) -> list[GradientTokenEntity]:
        result = await self._session.execute(
            select(GradientTokenModel).where(GradientTokenModel.project_id == project_id)
        )
        return [_to_entity(g) for g in result.scalars().all()]

    async def list_all(self, *, project_id: int | None) -> list[GradientTokenEntity]:
        query = select(GradientTokenModel)
        if project_id is not None:
            query = query.where(GradientTokenModel.project_id == project_id)
        result = await self._session.execute(query)
        return [_to_entity(g) for g in result.scalars().all()]
