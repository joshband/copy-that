from __future__ import annotations

from collections.abc import Mapping, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.color_tokens import ColorToken as ColorTokenEntity
from copy_that.infrastructure.persistence.models import ColorToken as ColorTokenModel


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


class SQLAlchemyColorTokenLibraryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_library_id(self, *, library_id: int) -> list[ColorTokenEntity]:
        result = await self._session.execute(
            select(ColorTokenModel).where(ColorTokenModel.library_id == library_id)
        )
        return [_to_entity(c) for c in result.scalars().all()]

    async def list_by_ids_for_library(
        self, *, library_id: int, token_ids: Sequence[int]
    ) -> list[ColorTokenEntity]:
        if not token_ids:
            return []
        result = await self._session.execute(
            select(ColorTokenModel)
            .where(ColorTokenModel.id.in_(list(token_ids)))
            .where(ColorTokenModel.library_id == library_id)
        )
        return [_to_entity(c) for c in result.scalars().all()]

    async def assign_roles(self, *, library_id: int, role_by_token_id: Mapping[int, str]) -> int:
        if not role_by_token_id:
            return 0
        token_ids = list(role_by_token_id.keys())
        result = await self._session.execute(
            select(ColorTokenModel)
            .where(ColorTokenModel.id.in_(token_ids))
            .where(ColorTokenModel.library_id == library_id)
        )
        tokens = result.scalars().all()
        updated = 0
        for token in tokens:
            new_role = role_by_token_id.get(token.id)
            if new_role is None:
                continue
            token.role = new_role
            updated += 1
        if updated:
            await self._session.commit()
        return updated
