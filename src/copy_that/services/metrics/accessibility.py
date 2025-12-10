"""Accessibility metrics provider - WCAG compliance and color safety.

Provides TIER 2 metrics: contrast ratios, WCAG compliance, colorblind safety.
Returns in ~100-200ms with pure mathematical analysis.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.color_utils import (
    calculate_wcag_contrast,
    relative_luminance,
)

from .base import MetricProvider, MetricResult, MetricTier
from .token_graph import TokenGraph

logger = logging.getLogger(__name__)


class AccessibilityMetricsProvider(MetricProvider):
    """Computes accessibility metrics (TIER 2) from extracted colors.

    Metrics computed:
    - WCAG contrast ratios (on white, black, custom backgrounds)
    - WCAG AA/AAA compliance (normal text, large text)
    - Colorblind safety assessment
    - Text role assignment (which colors work for text)
    - Contrast distribution analysis

    Time: ~100-200ms (color analysis + contrast calculations)

    Uses TokenGraph for generic token loading, but only analyzes color tokens.
    """

    name = "accessibility"
    tier = MetricTier.TIER_2

    def __init__(self, db: AsyncSession):
        """Initialize provider with database session.

        Args:
            db: AsyncSession for database access
        """
        self.db = db

    async def compute(self, project_id: int) -> MetricResult:
        """Compute accessibility metrics for a project.

        Args:
            project_id: Project to analyze

        Returns:
            MetricResult with accessibility metrics data
        """
        try:
            # Load tokens using TokenGraph (only load color category)
            graph = TokenGraph(project_id, self.db)
            await graph.load(categories=["color"])

            # Get color tokens
            color_nodes = graph.get_tokens_by_category("color")

            if not color_nodes:
                return MetricResult(
                    tier=self.tier,
                    provider_name=self.name,
                    data={
                        "colors_analyzed": 0,
                        "wcag_compliance": None,
                        "colorblind_safe": None,
                        "contrast_distribution": None,
                    },
                )

            # Extract hex colors from TokenNodes
            hex_colors = [node.value for node in color_nodes if node.value]

            wcag_compliance = self._analyze_wcag_compliance(hex_colors)
            colorblind_safety = self._analyze_colorblind_safety(hex_colors)
            contrast_distribution = self._analyze_contrast_distribution(hex_colors)
            text_role_analysis = self._analyze_text_roles(hex_colors)

            data = {
                "colors_analyzed": len(hex_colors),
                "wcag_compliance": wcag_compliance,
                "colorblind_safety": colorblind_safety,
                "contrast_distribution": contrast_distribution,
                "text_roles": text_role_analysis,
            }

            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                data=data,
            )

        except Exception as e:
            logger.error(f"Accessibility metrics computation failed: {e}", exc_info=True)
            return MetricResult(
                tier=self.tier,
                provider_name=self.name,
                error=str(e),
            )

    def _analyze_wcag_compliance(self, hex_colors: list[str]) -> dict[str, Any]:
        """Analyze WCAG contrast compliance for all color pairs.

        Args:
            hex_colors: List of hex color values

        Returns:
            Dict with compliance statistics
        """
        wcag_aa_pairs = 0
        wcag_aaa_pairs = 0
        contrast_ratios: list[float] = []

        for i, color1 in enumerate(hex_colors):
            for color2 in hex_colors[i + 1 :]:
                try:
                    ratio = calculate_wcag_contrast(color1, color2)
                    contrast_ratios.append(ratio)

                    if ratio >= 4.5:  # AA large text / AAA normal text
                        wcag_aa_pairs += 1
                    if ratio >= 7.0:  # AAA normal text
                        wcag_aaa_pairs += 1
                except Exception:
                    continue

        return {
            "total_pairs": len(contrast_ratios),
            "aa_compliant_pairs": wcag_aa_pairs,
            "aaa_compliant_pairs": wcag_aaa_pairs,
            "aa_compliance_percentage": (
                (wcag_aa_pairs / len(contrast_ratios) * 100) if contrast_ratios else 0
            ),
            "aaa_compliance_percentage": (
                (wcag_aaa_pairs / len(contrast_ratios) * 100) if contrast_ratios else 0
            ),
            "min_contrast": min(contrast_ratios) if contrast_ratios else None,
            "max_contrast": max(contrast_ratios) if contrast_ratios else None,
            "avg_contrast": (
                sum(contrast_ratios) / len(contrast_ratios) if contrast_ratios else None
            ),
        }

    def _analyze_colorblind_safety(self, hex_colors: list[str]) -> dict[str, Any]:
        """Analyze colorblind safety of the palette.

        Args:
            hex_colors: List of hex color values

        Returns:
            Dict with colorblind safety analysis
        """
        # TODO: Enhance with ColorAide CVD simulation (Brettel/Machado algorithms)
        # For now: Simple check - do colors have sufficient saturation/distinctness?

        desaturated_count = 0
        grayscale_count = 0

        for hex_color in hex_colors:
            try:
                # Extract saturation (would use coloraide for proper CVD simulation)
                # For now: simple heuristic
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)

                max_c = max(r, g, b)
                min_c = min(r, g, b)
                delta = max_c - min_c

                # Grayscale if all channels are equal
                if delta < 10:
                    grayscale_count += 1
                # Desaturated if low saturation
                if max_c > 0 and delta / max_c < 0.2:
                    desaturated_count += 1
            except Exception:
                continue

        return {
            "total_colors": len(hex_colors),
            "grayscale_colors": grayscale_count,
            "low_saturation_colors": desaturated_count,
            "estimated_safe": grayscale_count == 0,  # Simplified check
            "note": "Uses luminance-based estimate. Run CVD simulation for precise analysis.",
        }

    def _analyze_contrast_distribution(self, hex_colors: list[str]) -> dict[str, Any]:
        """Analyze how contrast is distributed across the palette.

        Args:
            hex_colors: List of hex color values

        Returns:
            Dict with contrast distribution analysis
        """
        luminances: list[float] = []

        for hex_color in hex_colors:
            try:
                lum = relative_luminance(hex_color)
                luminances.append(lum)
            except Exception:
                continue

        if not luminances:
            return {
                "colors_analyzed": 0,
                "distribution": None,
            }

        luminances.sort()
        min_lum = min(luminances)
        max_lum = max(luminances)
        avg_lum = sum(luminances) / len(luminances)

        # Categorize by luminance thirds
        light = sum(1 for l in luminances if l > 0.66)
        medium = sum(1 for l in luminances if 0.33 <= l <= 0.66)
        dark = sum(1 for l in luminances if l < 0.33)

        return {
            "colors_analyzed": len(luminances),
            "min_luminance": round(min_lum, 3),
            "max_luminance": round(max_lum, 3),
            "avg_luminance": round(avg_lum, 3),
            "luminance_range": round(max_lum - min_lum, 3),
            "distribution": {
                "light_colors": light,
                "medium_colors": medium,
                "dark_colors": dark,
            },
            "well_distributed": (light > 0 and medium > 0 and dark > 0),
        }

    def _analyze_text_roles(self, hex_colors: list[str]) -> dict[str, Any]:
        """Analyze which colors work best for text on standard backgrounds.

        Args:
            hex_colors: List of hex color values

        Returns:
            Dict with text role analysis
        """
        white_background = "#FFFFFF"
        black_background = "#000000"

        text_on_white = []
        text_on_black = []

        for hex_color in hex_colors:
            try:
                contrast_white = calculate_wcag_contrast(hex_color, white_background)
                contrast_black = calculate_wcag_contrast(hex_color, black_background)

                # Text needs contrast >= 4.5:1 for AA
                if contrast_white >= 4.5:
                    text_on_white.append(hex_color)
                if contrast_black >= 4.5:
                    text_on_black.append(hex_color)
            except Exception:
                continue

        return {
            "suitable_text_on_white": len(text_on_white),
            "suitable_text_on_black": len(text_on_black),
            "suitable_for_both": len(set(text_on_white) & set(text_on_black)),
            "text_on_white_colors": text_on_white[:5],  # Top 5 examples
            "text_on_black_colors": text_on_black[:5],  # Top 5 examples
        }
