"""
Integration of shadowlab image shadow analysis with Copy-That token system.

This module bridges shadowlab's geometric shadow analysis with the existing
design token infrastructure, enabling shadow features extracted from general
images to be stored and managed as first-class design tokens.

Shadow tokens from this module include:
- Light direction and quality (directional, diffuse, rim, etc.)
- Shadow softness (hard, medium, soft, very soft)
- Shadow density/coverage
- Shadow contrast
- Intensity characteristics

These are distinct from UI shadow tokens (CSS box-shadows) and represent
actual illumination and shadow characteristics that can inform design systems.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ShadowTokenIntegration:
    """Bridge between shadowlab analysis and Copy-That token system."""

    @staticmethod
    def analysis_to_token_metadata(
        analysis: dict[str, Any],
        image_id: str,
        image_source: str = "extracted_image",
    ) -> dict[str, Any]:
        """
        Convert shadowlab analysis results into token system metadata.

        Args:
            analysis: Result from analyze_image_for_shadows()
            image_id: Identifier for source image
            image_source: Source label (extracted_image, screenshot, photograph, etc.)

        Returns:
            Dictionary suitable for storing in ShadowToken.extraction_metadata (JSON)

        Structure:
            {
              "analysis_version": "1.0",
              "image_id": "img_12345",
              "image_source": "extracted_image",
              "features": { numeric features },
              "tokens": { categorical tokens },
              "geometry": { depth/normals/shading data },
              "confidence_metrics": { confidence scores },
            }
        """
        features = analysis.get("features", {})
        tokens = analysis.get("tokens", {})

        metadata = {
            "analysis_version": "1.0",
            "image_id": image_id,
            "image_source": image_source,
            "extracted_at": None,  # Will be set by caller with datetime
            # Numeric features
            "features": {
                "shadow_area_fraction": features.get("shadow_area_fraction", 0),
                "mean_shadow_intensity": features.get("mean_shadow_intensity", 0),
                "mean_lit_intensity": features.get("mean_lit_intensity", 0),
                "edge_softness_mean": features.get("edge_softness_mean", 0),
                "shadow_contrast": features.get("shadow_contrast", 0),
                "shadow_count_major": features.get("shadow_count_major", 0),
                "inconsistency_score": features.get("inconsistency_score", 0),
            },
            # Categorical tokens
            "tokens": {
                "style_key_direction": tokens.get("style_key_direction", "unknown"),
                "style_softness": tokens.get("style_softness", "unknown"),
                "style_contrast": tokens.get("style_contrast", "unknown"),
                "style_density": tokens.get("style_density", "unknown"),
                "intensity_shadow": tokens.get("intensity_shadow", "unknown"),
                "intensity_lit": tokens.get("intensity_lit", "unknown"),
                "lighting_style": tokens.get("lighting_style", "unknown"),
            },
            # Light direction (if available)
            "light_direction": None,
            "light_direction_confidence": features.get("light_direction_confidence", 0),
        }

        # Store light direction if available
        light_dir = features.get("dominant_light_direction")
        if light_dir is not None:
            azimuth, elevation = light_dir
            metadata["light_direction"] = {
                "azimuth_radians": float(azimuth),
                "elevation_radians": float(elevation),
                "azimuth_degrees": float(azimuth * 180 / 3.14159),
                "elevation_degrees": float(elevation * 180 / 3.14159),
            }

        return metadata

    @staticmethod
    def create_shadow_style_token(
        analysis: dict[str, Any],
        image_id: str,
        project_id: int,
        semantic_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a shadow style token from analysis (for token library integration).

        This creates a high-level token representing the overall shadow/lighting
        style of an image, suitable for design system use.

        Args:
            analysis: Result from analyze_image_for_shadows()
            image_id: Source image ID
            project_id: Project ID for storage
            semantic_name: Optional friendly name (auto-generated if None)

        Returns:
            Dictionary with fields suitable for token storage:
                {
                  "token_type": "shadow.style",
                  "semantic_name": "harsh-overhead-lighting",
                  "style_key_direction": "overhead",
                  "style_softness": "hard",
                  "style_contrast": "high",
                  "style_density": "moderate",
                  "lighting_style": "directional",
                  "confidence": 0.85,
                  "source_image_id": "img_12345",
                  "metadata": { ... },
                }
        """
        tokens = analysis.get("tokens", {})

        # Auto-generate semantic name if not provided
        if semantic_name is None:
            direction = tokens.get("style_key_direction", "unknown")
            softness = tokens.get("style_softness", "unknown")
            lighting = tokens.get("lighting_style", "unknown")
            semantic_name = f"{lighting}-{softness}-{direction}"

        metadata = ShadowTokenIntegration.analysis_to_token_metadata(
            analysis,
            image_id,
        )

        return {
            "token_type": "shadow.lighting_style",
            "semantic_name": semantic_name,
            "category": "shadow",
            "token_group": "lighting_and_atmosphere",
            # Shadow characteristics
            "style_key_direction": tokens.get("style_key_direction", "unknown"),
            "style_softness": tokens.get("style_softness", "unknown"),
            "style_contrast": tokens.get("style_contrast", "unknown"),
            "style_density": tokens.get("style_density", "unknown"),
            "lighting_style": tokens.get("lighting_style", "unknown"),
            # Quality metrics
            "extraction_confidence": tokens.get("extraction_confidence", 0),
            "source_image_id": image_id,
            "project_id": project_id,
            # Metadata for token graph
            "metadata": metadata,
        }

    @staticmethod
    def create_individual_shadow_tokens(
        analysis: dict[str, Any],
        image_id: str,
        project_id: int,
    ) -> list[dict[str, Any]]:
        """
        Create individual shadow tokens for each aspect of the analysis.

        Creates tokens for shadow intensity, edge characteristics, and other
        measurable properties.

        Args:
            analysis: Result from analyze_image_for_shadows()
            image_id: Source image ID
            project_id: Project ID

        Returns:
            List of token dictionaries, each representing a shadow characteristic
        """
        tokens = analysis.get("tokens", {})
        features = analysis.get("features", {})

        token_list = []

        # Token 1: Shadow intensity
        token_list.append(
            {
                "token_type": "shadow.intensity",
                "semantic_name": f"shadow-intensity-{tokens.get('intensity_shadow', 'unknown')}",
                "token_subtype": "intensity",
                "value": tokens.get("intensity_shadow", "unknown"),
                "numeric_value": features.get("mean_shadow_intensity", 0),
                "source_image_id": image_id,
                "project_id": project_id,
            }
        )

        # Token 2: Light intensity (contrast with shadows)
        token_list.append(
            {
                "token_type": "shadow.light_intensity",
                "semantic_name": f"light-intensity-{tokens.get('intensity_lit', 'unknown')}",
                "token_subtype": "intensity",
                "value": tokens.get("intensity_lit", "unknown"),
                "numeric_value": features.get("mean_lit_intensity", 0),
                "source_image_id": image_id,
                "project_id": project_id,
            }
        )

        # Token 3: Edge softness
        token_list.append(
            {
                "token_type": "shadow.edge_softness",
                "semantic_name": f"shadow-edges-{tokens.get('style_softness', 'unknown')}",
                "token_subtype": "softness",
                "value": tokens.get("style_softness", "unknown"),
                "numeric_value": features.get("edge_softness_mean", 0),
                "source_image_id": image_id,
                "project_id": project_id,
            }
        )

        # Token 4: Shadow coverage/density
        token_list.append(
            {
                "token_type": "shadow.coverage",
                "semantic_name": f"shadow-coverage-{tokens.get('style_density', 'unknown')}",
                "token_subtype": "density",
                "value": tokens.get("style_density", "unknown"),
                "numeric_value": features.get("shadow_area_fraction", 0),
                "source_image_id": image_id,
                "project_id": project_id,
            }
        )

        # Token 5: Light direction (if available)
        light_dir = features.get("dominant_light_direction")
        if light_dir is not None:
            azimuth, elevation = light_dir
            token_list.append(
                {
                    "token_type": "shadow.light_direction",
                    "semantic_name": f"light-from-{tokens.get('style_key_direction', 'unknown')}",
                    "token_subtype": "direction",
                    "value": tokens.get("style_key_direction", "unknown"),
                    "azimuth_radians": float(azimuth),
                    "elevation_radians": float(elevation),
                    "confidence": features.get("light_direction_confidence", 0),
                    "source_image_id": image_id,
                    "project_id": project_id,
                }
            )

        return token_list

    @staticmethod
    def suggest_css_box_shadow(
        analysis: dict[str, Any],
    ) -> dict[str, str]:
        """
        Generate CSS box-shadow values based on geometric shadow analysis.

        Translates shadowlab's geometric analysis into practical CSS that
        can be used for UI design.

        Args:
            analysis: Result from analyze_image_for_shadows()

        Returns:
            Dictionary with CSS shadow preset suggestions:
                {
                  "subtle": "0 2px 4px rgba(...)",
                  "medium": "0 4px 8px rgba(...)",
                  "strong": "0 8px 16px rgba(...)",
                  "based_on": "lighting_style",
                }

        Notes:
            - Shadow color is approximated based on intensity
            - Blur/spread inferred from softness characteristics
            - Opacity derived from shadow contrast
        """
        tokens = analysis.get("tokens", {})
        features = analysis.get("features", {})

        # Color: darker if high contrast shadows
        shadow_intensity = features.get("mean_shadow_intensity", 0.3)
        shadow_opacity = min(0.5, (1 - shadow_intensity) * 0.6)
        shadow_color = f"rgba(0, 0, 0, {shadow_opacity:.2f})"

        # Blur and spread based on softness
        softness = tokens.get("style_softness", "medium")
        blur_spread_map = {
            "very_hard": ("1px", "0px"),
            "hard": ("2px", "1px"),
            "medium": ("4px", "2px"),
            "soft": ("8px", "4px"),
            "very_soft": ("16px", "8px"),
        }
        blur, spread = blur_spread_map.get(softness, ("4px", "2px"))

        # Shadow offset based on light direction
        direction = tokens.get("style_key_direction", "unknown")
        offset_map = {
            "upper_left": ("-2px", "-2px"),
            "upper_right": ("2px", "-2px"),
            "lower_left": ("-2px", "2px"),
            "lower_right": ("2px", "2px"),
            "left": ("-4px", "0px"),
            "right": ("4px", "0px"),
            "overhead": ("0px", "-4px"),
            "front": ("0px", "4px"),
            "unknown": ("0px", "2px"),
        }
        offset_x, offset_y = offset_map.get(direction, ("0px", "4px"))

        # Generate CSS variants based on coverage density
        density = tokens.get("style_density", "moderate")
        variants = {
            "subtle": f"{offset_x} {offset_y} {blur} {shadow_color}",
            "medium": f"{offset_x} {offset_y} {blur} {spread} {shadow_color}",
            "strong": f"{offset_x} {offset_y} {blur} {spread} {shadow_color}, 0 0 {blur} {shadow_color}",
        }

        return {
            "subtle": variants["subtle"],
            "medium": variants["medium"],
            "strong": variants["strong"],
            "based_on": "shadowlab_geometric_analysis",
            "direction": direction,
            "softness": softness,
            "density": density,
        }

    @staticmethod
    def validate_analysis_for_storage(
        analysis: dict[str, Any],
        min_confidence: float = 0.3,
    ) -> tuple[bool, str | None]:
        """
        Validate that an analysis result is suitable for token storage.

        Args:
            analysis: Result from analyze_image_for_shadows()
            min_confidence: Minimum acceptable confidence (0..1)

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if suitable for storage
            - error_message: None if valid, otherwise describes issue
        """
        # Check for required keys
        if not analysis:
            return False, "Analysis dict is empty"

        if "features" not in analysis:
            return False, "Missing 'features' in analysis"

        if "tokens" not in analysis:
            return False, "Missing 'tokens' in analysis"

        # Check confidence
        features = analysis["features"]
        tokens = analysis["tokens"]

        confidence = tokens.get("extraction_confidence", 0)
        if confidence < min_confidence:
            return False, f"Confidence {confidence:.2f} below threshold {min_confidence}"

        # Check for NaN or invalid values
        for key, value in features.items():
            if isinstance(value, float) and (value != value or abs(value) > 1e10):  # Check for NaN
                return False, f"Invalid feature value for {key}: {value}"

        return True, None
