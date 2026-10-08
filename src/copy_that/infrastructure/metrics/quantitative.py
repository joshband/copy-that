"""Quantitative metrics provider - fast, deterministic analysis.

Provides TIER 1 metrics: color, spacing, typography, and system organization analysis.
Returns in <100ms with pure mathematical analysis (no AI involved).
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.services.overview_metrics_service import infer_metrics

from .base import MetricProvider, MetricResult, MetricTier
from .token_graph import TokenGraph, TokenNode

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

    Uses TokenGraph for generic token loading, supporting ANY token type.
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
            # Load all tokens using TokenGraph
            graph = TokenGraph(project_id, self.db)
            await graph.load()

            # Get tokens by category (works with ANY category)
            colors = self._convert_nodes_to_models(graph.get_tokens_by_category("color"))
            spacing = self._convert_nodes_to_models(graph.get_tokens_by_category("spacing"))
            typography = self._convert_nodes_to_models(graph.get_tokens_by_category("typography"))
            shadows = self._convert_nodes_to_models(graph.get_tokens_by_category("shadow"))

            # Analyze tokens using existing service
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

    def _convert_nodes_to_models(self, nodes: list[TokenNode]) -> list[Any]:
        """Convert TokenNodes to model-like objects for compatibility.

        The infer_metrics service expects objects with specific attributes.
        TokenNodes store all data in metadata, so we create simple objects
        with the expected attributes.

        Args:
            nodes: List of TokenNodes

        Returns:
            List of objects with token attributes
        """

        class TokenProxy:
            """Proxy object that exposes TokenNode data as attributes."""

            def __init__(self, node: TokenNode):
                self._node = node
                # Expose value as primary attribute
                if isinstance(node.value, dict):
                    for key, val in node.value.items():
                        setattr(self, key, val)
                else:
                    # For simple values (hex, value_px, etc.)
                    if node.category == "color":
                        self.hex = node.value
                    elif node.category == "spacing":
                        self.value_px = node.value
                    elif node.category == "font_size":
                        self.size_px = node.value

                # Expose all metadata as attributes
                for key, val in node.metadata.items():
                    setattr(self, key, val)

        return [TokenProxy(node) for node in nodes]
