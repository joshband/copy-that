from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.color_tokens import ColorToken as ColorTokenEntity
from copy_that.domain.color_tokens import ColorTokenCreate
from copy_that.infrastructure.persistence.models import ColorToken as ColorTokenModel
from copy_that.infrastructure.persistence.models import ExtractionJob


def _to_entity(model: ColorTokenModel) -> ColorTokenEntity:
    return ColorTokenEntity(
        id=model.id,
        project_id=model.project_id,
        extraction_job_id=model.extraction_job_id,
        library_id=model.library_id,
        role=model.role,
        hex=model.hex,
        rgb=model.rgb,
        hsl=model.hsl,
        hsv=model.hsv,
        name=model.name,
        design_intent=model.design_intent,
        semantic_names=model.semantic_names,
        extraction_metadata=model.extraction_metadata,
        category=model.category,
        confidence=model.confidence,
        harmony=model.harmony,
        harmony_confidence=model.harmony_confidence,
        hue_angles=model.hue_angles,
        temperature=model.temperature,
        saturation_level=model.saturation_level,
        lightness_level=model.lightness_level,
        usage=model.usage,
        count=model.count,
        prominence_percentage=model.prominence_percentage,
        wcag_contrast_on_white=model.wcag_contrast_on_white,
        wcag_contrast_on_black=model.wcag_contrast_on_black,
        wcag_aa_compliant_text=model.wcag_aa_compliant_text,
        wcag_aaa_compliant_text=model.wcag_aaa_compliant_text,
        wcag_aa_compliant_normal=model.wcag_aa_compliant_normal,
        wcag_aaa_compliant_normal=model.wcag_aaa_compliant_normal,
        colorblind_safe=model.colorblind_safe,
        tint_color=model.tint_color,
        shade_color=model.shade_color,
        tone_color=model.tone_color,
        closest_web_safe=model.closest_web_safe,
        closest_css_named=model.closest_css_named,
        delta_e_to_dominant=model.delta_e_to_dominant,
        is_neutral=model.is_neutral,
        background_role=model.background_role,
        foreground_role=model.foreground_role,
        contrast_category=model.contrast_category,
        is_accent=model.is_accent,
        state_variants=model.state_variants,
        kmeans_cluster_id=model.kmeans_cluster_id,
        sam_segmentation_mask=model.sam_segmentation_mask,
        clip_embeddings=model.clip_embeddings,
        histogram_significance=model.histogram_significance,
        provenance=model.provenance,
        created_at=model.created_at,
    )


class SQLAlchemyColorTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        tokens: Sequence[ColorTokenCreate],
        result_data: dict[str, object],
    ) -> int:
        job = ExtractionJob(
            project_id=project_id,
            source_url=source_url,
            extraction_type="color",
            status="completed",
            result_data=json.dumps(result_data, default=str),
        )
        self._session.add(job)
        await self._session.flush()

        for token in tokens:
            self._session.add(
                ColorTokenModel(
                    project_id=project_id,
                    extraction_job_id=job.id,
                    hex=token.hex,
                    rgb=token.rgb,
                    hsl=token.hsl,
                    hsv=token.hsv,
                    name=token.name,
                    design_intent=token.design_intent,
                    semantic_names=token.semantic_names,
                    extraction_metadata=token.extraction_metadata,
                    category=token.category,
                    confidence=token.confidence,
                    harmony=token.harmony,
                    harmony_confidence=token.harmony_confidence,
                    hue_angles=token.hue_angles,
                    temperature=token.temperature,
                    saturation_level=token.saturation_level,
                    lightness_level=token.lightness_level,
                    usage=token.usage,
                    count=token.count,
                    prominence_percentage=token.prominence_percentage,
                    wcag_contrast_on_white=token.wcag_contrast_on_white,
                    wcag_contrast_on_black=token.wcag_contrast_on_black,
                    wcag_aa_compliant_text=token.wcag_aa_compliant_text,
                    wcag_aaa_compliant_text=token.wcag_aaa_compliant_text,
                    wcag_aa_compliant_normal=token.wcag_aa_compliant_normal,
                    wcag_aaa_compliant_normal=token.wcag_aaa_compliant_normal,
                    colorblind_safe=token.colorblind_safe,
                    tint_color=token.tint_color,
                    shade_color=token.shade_color,
                    tone_color=token.tone_color,
                    closest_web_safe=token.closest_web_safe,
                    closest_css_named=token.closest_css_named,
                    delta_e_to_dominant=token.delta_e_to_dominant,
                    is_neutral=token.is_neutral,
                    background_role=token.background_role,
                    foreground_role=token.foreground_role,
                    contrast_category=token.contrast_category,
                    is_accent=token.is_accent,
                    state_variants=token.state_variants,
                    kmeans_cluster_id=token.kmeans_cluster_id,
                    sam_segmentation_mask=token.sam_segmentation_mask,
                    clip_embeddings=token.clip_embeddings,
                    histogram_significance=token.histogram_significance,
                    library_id=token.library_id,
                    role=token.role,
                    provenance=token.provenance,
                )
            )

        await self._session.commit()
        return int(job.id)

    async def list_by_project(self, *, project_id: int) -> list[ColorTokenEntity]:
        result = await self._session.execute(
            select(ColorTokenModel)
            .where(ColorTokenModel.project_id == project_id)
            .order_by(ColorTokenModel.created_at.desc())
        )
        return [_to_entity(c) for c in result.scalars().all()]

    async def list_all(self, *, project_id: int | None) -> list[ColorTokenEntity]:
        query = select(ColorTokenModel)
        if project_id is not None:
            query = query.where(ColorTokenModel.project_id == project_id)
        result = await self._session.execute(query)
        return [_to_entity(c) for c in result.scalars().all()]

    async def list_by_job(self, *, extraction_job_id: int) -> list[ColorTokenEntity]:
        result = await self._session.execute(
            select(ColorTokenModel)
            .where(ColorTokenModel.extraction_job_id == extraction_job_id)
            .order_by(ColorTokenModel.id.asc())
        )
        return [_to_entity(c) for c in result.scalars().all()]

    async def get(self, *, color_id: int) -> ColorTokenEntity | None:
        result = await self._session.execute(
            select(ColorTokenModel).where(ColorTokenModel.id == color_id)
        )
        color = result.scalar_one_or_none()
        return _to_entity(color) if color else None

    async def create(
        self, *, project_id: int, extraction_job_id: int | None, token: ColorTokenCreate
    ) -> ColorTokenEntity:
        model = ColorTokenModel(
            project_id=project_id,
            extraction_job_id=extraction_job_id,
            hex=token.hex,
            rgb=token.rgb,
            hsl=token.hsl,
            hsv=token.hsv,
            name=token.name,
            design_intent=token.design_intent,
            semantic_names=token.semantic_names,
            extraction_metadata=token.extraction_metadata,
            category=token.category,
            confidence=token.confidence or 0.0,
            harmony=token.harmony,
            harmony_confidence=token.harmony_confidence,
            hue_angles=token.hue_angles,
            temperature=token.temperature,
            saturation_level=token.saturation_level,
            lightness_level=token.lightness_level,
            usage=token.usage,
            count=token.count or 1,
            prominence_percentage=token.prominence_percentage,
            wcag_contrast_on_white=token.wcag_contrast_on_white,
            wcag_contrast_on_black=token.wcag_contrast_on_black,
            wcag_aa_compliant_text=token.wcag_aa_compliant_text,
            wcag_aaa_compliant_text=token.wcag_aaa_compliant_text,
            wcag_aa_compliant_normal=token.wcag_aa_compliant_normal,
            wcag_aaa_compliant_normal=token.wcag_aaa_compliant_normal,
            colorblind_safe=token.colorblind_safe,
            tint_color=token.tint_color,
            shade_color=token.shade_color,
            tone_color=token.tone_color,
            closest_web_safe=token.closest_web_safe,
            closest_css_named=token.closest_css_named,
            delta_e_to_dominant=token.delta_e_to_dominant,
            is_neutral=token.is_neutral,
            background_role=token.background_role,
            foreground_role=token.foreground_role,
            contrast_category=token.contrast_category,
            is_accent=token.is_accent,
            state_variants=token.state_variants,
            kmeans_cluster_id=token.kmeans_cluster_id,
            sam_segmentation_mask=token.sam_segmentation_mask,
            clip_embeddings=token.clip_embeddings,
            histogram_significance=token.histogram_significance,
            library_id=token.library_id,
            role=token.role,
            provenance=token.provenance,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(
        self,
        *,
        color_id: int,
        semantic_names: str | None,
        design_intent: str | None,
    ) -> ColorTokenEntity | None:
        result = await self._session.execute(
            select(ColorTokenModel).where(ColorTokenModel.id == color_id)
        )
        color = result.scalar_one_or_none()
        if not color:
            return None

        if semantic_names is not None:
            color.semantic_names = semantic_names
        if design_intent is not None:
            color.design_intent = design_intent

        self._session.add(color)
        await self._session.commit()
        await self._session.refresh(color)
        return _to_entity(color)
