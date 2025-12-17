from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.typography import TypographyToken as TypographyTokenEntity
from copy_that.domain.typography import TypographyTokenCreate
from copy_that.infrastructure.persistence.models import ExtractionJob
from copy_that.infrastructure.persistence.models import TypographyToken as TypographyTokenModel


def _to_entity(model: TypographyTokenModel) -> TypographyTokenEntity:
    return TypographyTokenEntity(
        id=model.id,
        project_id=model.project_id,
        extraction_job_id=model.extraction_job_id,
        font_family=model.font_family,
        font_weight=model.font_weight,
        font_size=model.font_size,
        line_height=model.line_height,
        letter_spacing=model.letter_spacing,
        text_transform=model.text_transform,
        name=model.name,
        semantic_role=model.semantic_role,
        category=model.category,
        confidence=model.confidence,
        prominence=model.prominence,
        is_readable=model.is_readable,
        readability_score=model.readability_score,
        extraction_metadata=model.extraction_metadata,
        usage=model.usage,
        created_at=model.created_at,
    )


class SQLAlchemyTypographyTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        tokens: Sequence[TypographyTokenCreate],
        result_data: dict[str, object],
    ) -> int:
        job = ExtractionJob(
            project_id=project_id,
            source_url=source_url,
            extraction_type="typography",
            status="completed",
            result_data=json.dumps(result_data, default=str),
        )
        self._session.add(job)
        await self._session.flush()

        for token in tokens:
            self._session.add(
                TypographyTokenModel(
                    project_id=project_id,
                    extraction_job_id=job.id,
                    font_family=token.font_family,
                    font_weight=token.font_weight,
                    font_size=token.font_size,
                    line_height=token.line_height,
                    letter_spacing=token.letter_spacing,
                    text_transform=token.text_transform,
                    semantic_role=token.semantic_role,
                    category=token.category,
                    name=token.name,
                    confidence=token.confidence,
                    prominence=token.prominence,
                    is_readable=token.is_readable,
                    readability_score=token.readability_score,
                    extraction_metadata=token.extraction_metadata,
                )
            )

        await self._session.commit()
        return int(job.id)

    async def list_by_project(self, *, project_id: int) -> list[TypographyTokenEntity]:
        result = await self._session.execute(
            select(TypographyTokenModel)
            .where(TypographyTokenModel.project_id == project_id)
            .order_by(TypographyTokenModel.created_at.desc())
        )
        return [_to_entity(t) for t in result.scalars().all()]

    async def list_all(self, *, project_id: int | None) -> list[TypographyTokenEntity]:
        query = select(TypographyTokenModel)
        if project_id is not None:
            query = query.where(TypographyTokenModel.project_id == project_id)
        result = await self._session.execute(query)
        return [_to_entity(t) for t in result.scalars().all()]

    async def create(self, *, token: TypographyTokenCreate) -> TypographyTokenEntity:
        model = TypographyTokenModel(
            project_id=token.project_id,
            extraction_job_id=token.extraction_job_id,
            font_family=token.font_family,
            font_weight=token.font_weight,
            font_size=token.font_size,
            line_height=token.line_height,
            letter_spacing=token.letter_spacing,
            text_transform=token.text_transform,
            semantic_role=token.semantic_role,
            category=token.category,
            name=token.name,
            confidence=token.confidence,
            prominence=token.prominence,
            is_readable=token.is_readable,
            readability_score=token.readability_score,
            extraction_metadata=token.extraction_metadata,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get(self, *, token_id: int) -> TypographyTokenEntity | None:
        result = await self._session.execute(
            select(TypographyTokenModel).where(TypographyTokenModel.id == token_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update(
        self,
        *,
        token_id: int,
        token: TypographyTokenCreate,
    ) -> TypographyTokenEntity | None:
        result = await self._session.execute(
            select(TypographyTokenModel).where(TypographyTokenModel.id == token_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        model.font_family = token.font_family
        model.font_weight = token.font_weight
        model.font_size = token.font_size
        model.line_height = token.line_height
        model.letter_spacing = token.letter_spacing
        model.text_transform = token.text_transform
        model.semantic_role = token.semantic_role
        model.category = token.category
        model.name = token.name
        model.confidence = token.confidence
        model.prominence = token.prominence
        model.is_readable = token.is_readable
        model.readability_score = token.readability_score
        model.extraction_metadata = token.extraction_metadata

        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, *, token_id: int) -> bool:
        result = await self._session.execute(
            select(TypographyTokenModel).where(TypographyTokenModel.id == token_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self._session.delete(model)
        await self._session.commit()
        return True
