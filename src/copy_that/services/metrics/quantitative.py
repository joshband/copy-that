"""Quantitative metrics provider - fast, deterministic analysis.

Provides TIER 1 metrics: color, spacing, typography, and system organization analysis.
Returns in <100ms with pure mathematical analysis (no AI involved).
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import ColorToken, ShadowToken, SpacingToken, TypographyToken
from copy_that.services.overview_metrics_service import infer_metrics

from .base import MetricProvider, MetricResult, MetricTier

logger = logging.getLogger(__name__)


class QuantitativeMetricsProvider(MetricProvider):
    """Computes quantitative metrics (TIER 1) from extracted tokens.

    Metrics computed:
    - Color system characteristics (palette type, temperature, harmony)
    - Spacing system (scale type, uniformity)
    - Typography system (hierarchy depth, scale type)
    - Shadow system (count, distribution)
    - Overall design system maturity and organization quality

    Time: ~50-100ms (database fetch + analysis)
    """

    name = "quantitative"
    tier = MetricTier.TIER_1

    def __init__(self, db: AsyncSession):
        """Initialize provider with database session.

        Args:
            db: AsyncSession for database access
        """
        self.db = db

    async def compute(self, project_id: int) -> MetricResult:
        """Compute quantitative metrics for a project.

        Args:
            project_id: Project to analyze

        Returns:
            MetricResult with quantitative metrics data
        """
        try:
            # Fetch extracted tokens from database
            colors = await self._fetch_colors(project_id)
            spacing = await self._fetch_spacing(project_id)
            typography = await self._fetch_typography(project_id)
            shadows = await self._fetch_shadows(project_id)

            # Analyze tokens
            metrics = infer_metrics(colors, spacing, typography, shadows)

            # Extract only quantitative fields (exclude elaborated metrics)
            data = {
                "color": {
                    "palette_type": metrics.color_palette_type,
                    "temperature": metrics.color_temperature,
                    "harmony_type": metrics.color_harmony_type,
                    "count": len(colors),
                },
                "spacing": {
                    "scale_system": metrics.spacing_scale_system,
                    "uniformity": metrics.spacing_uniformity,
                    "count": len(spacing),
                },
                "typography": {
                    "hierarchy_depth": metrics.typography_hierarchy_depth,
                    "scale_type": metrics.typography_scale_type,
                    "count": len(typography),
                },
                "shadows": {
                    "count": len(shadows) if shadows else 0,
                },
                "system": {
                    "maturity": metrics.design_system_maturity,
                    "organization_quality": metrics.token_organization_quality,
                    "total_tokens": len(colors)
                    + len(spacing)
                    + len(typography)
                    + (len(shadows) if shadows else 0),
                },
            }

            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                data=data,
            )

        except Exception as e:
            logger.error(f"Quantitative metrics computation failed: {e}", exc_info=True)
            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                error=str(e),
            )

    async def _fetch_colors(self, project_id: int) -> list[Any]:
        """Fetch color tokens for a project.

        Args:
            project_id: Project ID

        Returns:
            List of color tokens
        """
        from sqlalchemy import select

        query = select(ColorToken).where(ColorToken.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _fetch_spacing(self, project_id: int) -> list[Any]:
        """Fetch spacing tokens for a project.

        Args:
            project_id: Project ID

        Returns:
            List of spacing tokens
        """
        from sqlalchemy import select

        query = select(SpacingToken).where(SpacingToken.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _fetch_typography(self, project_id: int) -> list[Any]:
        """Fetch typography tokens for a project.

        Args:
            project_id: Project ID

        Returns:
            List of typography tokens
        """
        from sqlalchemy import select

        query = select(TypographyToken).where(TypographyToken.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _fetch_shadows(self, project_id: int) -> list[Any]:
        """Fetch shadow tokens for a project.

        Args:
            project_id: Project ID

        Returns:
            List of shadow tokens
        """
        from sqlalchemy import select

        query = select(ShadowToken).where(ShadowToken.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalars().all()
