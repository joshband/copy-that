from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.shadows import ShadowToken as ShadowTokenEntity
from copy_that.domain.shadows import ShadowTokenCreate
from copy_that.infrastructure.persistence.models import ExtractionJob
from copy_that.infrastructure.persistence.models import ShadowToken as ShadowTokenModel


def _to_entity(model: ShadowTokenModel) -> ShadowTokenEntity:
    return ShadowTokenEntity(
        id=model.id,
        project_id=model.project_id,
        extraction_job_id=model.extraction_job_id,
        x_offset=model.x_offset,
        y_offset=model.y_offset,
        blur_radius=model.blur_radius,
        spread_radius=model.spread_radius,
        color_hex=model.color_hex,
        opacity=model.opacity,
        name=model.name,
        shadow_type=model.shadow_type,
        semantic_role=model.semantic_role,
        confidence=model.confidence,
        extraction_metadata=model.extraction_metadata,
        usage=model.usage,
        category=model.category,
        created_at=model.created_at,
    )


class SQLAlchemyShadowTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        shadows: Sequence[ShadowTokenCreate],
    ) -> int:
        job = ExtractionJob(
            project_id=project_id,
            source_url=source_url,
            extraction_type="shadow",
            status="completed",
            result_data=json.dumps({"token_count": len(shadows)}),
        )
        self._session.add(job)
        await self._session.flush()

        for shadow in shadows:
            self._session.add(
                ShadowTokenModel(
                    project_id=project_id,
                    extraction_job_id=job.id,
                    x_offset=shadow.x_offset,
                    y_offset=shadow.y_offset,
                    blur_radius=shadow.blur_radius,
                    spread_radius=shadow.spread_radius,
                    color_hex=shadow.color_hex,
                    opacity=shadow.opacity,
                    name=shadow.name,
                    shadow_type=shadow.shadow_type,
                    semantic_role=shadow.semantic_role,
                    confidence=shadow.confidence,
                    extraction_metadata=shadow.extraction_metadata,
                    usage=shadow.usage,
                    category=shadow.category,
                )
            )

        await self._session.commit()
        return int(job.id)

    async def list_by_project(self, *, project_id: int) -> list[ShadowTokenEntity]:
        result = await self._session.execute(
            select(ShadowTokenModel).where(ShadowTokenModel.project_id == project_id)
        )
        return [_to_entity(s) for s in result.scalars().all()]

    async def list_all(self, *, project_id: int | None) -> list[ShadowTokenEntity]:
        query = select(ShadowTokenModel)
        if project_id is not None:
            query = query.where(ShadowTokenModel.project_id == project_id)
        result = await self._session.execute(query)
        return [_to_entity(s) for s in result.scalars().all()]

    async def get(self, *, shadow_id: int) -> ShadowTokenEntity | None:
        result = await self._session.execute(
            select(ShadowTokenModel).where(ShadowTokenModel.id == shadow_id)
        )
        shadow = result.scalar_one_or_none()
        return _to_entity(shadow) if shadow else None

    async def update(
        self,
        *,
        shadow_id: int,
        name: str | None,
        semantic_role: str | None,
        shadow_type: str | None,
        confidence: float | None,
    ) -> ShadowTokenEntity | None:
        result = await self._session.execute(
            select(ShadowTokenModel).where(ShadowTokenModel.id == shadow_id)
        )
        shadow = result.scalar_one_or_none()
        if not shadow:
            return None

        if name is not None:
            shadow.name = name
        if semantic_role is not None:
            shadow.semantic_role = semantic_role
        if shadow_type is not None:
            shadow.shadow_type = shadow_type
        if confidence is not None:
            shadow.confidence = confidence

        self._session.add(shadow)
        await self._session.commit()
        await self._session.refresh(shadow)
        return _to_entity(shadow)

    async def delete(self, *, shadow_id: int) -> bool:
        result = await self._session.execute(
            select(ShadowTokenModel).where(ShadowTokenModel.id == shadow_id)
        )
        shadow = result.scalar_one_or_none()
        if not shadow:
            return False

        await self._session.delete(shadow)
        await self._session.commit()
        return True
