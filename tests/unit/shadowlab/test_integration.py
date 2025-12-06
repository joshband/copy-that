"""Tests for shadow token integration (shadowlab.integration)."""

import numpy as np
import pytest

from copy_that.shadowlab.integration import ShadowTokenIntegration


class TestAnalysisToTokenMetadata:
    """Test conversion of analysis to token metadata."""

    def test_basic_conversion(self):
        """Test basic analysis to metadata conversion."""
        analysis = {
            "features": {
                "shadow_area_fraction": 0.25,
                "mean_shadow_intensity": 0.3,
                "mean_lit_intensity": 0.8,
                "edge_softness_mean": 5.0,
            },
            "tokens": {
                "style_key_direction": "upper_left",
                "style_softness": "soft",
                "style_contrast": "medium",
                "style_density": "moderate",
            },
        }

        metadata = ShadowTokenIntegration.analysis_to_token_metadata(
            analysis, image_id="test_img_001"
        )

        assert metadata["image_id"] == "test_img_001"
        assert metadata["analysis_version"] == "1.0"
        assert metadata["features"]["shadow_area_fraction"] == 0.25
        assert metadata["tokens"]["style_key_direction"] == "upper_left"

    def test_with_light_direction(self):
        """Test metadata includes light direction when available."""
        analysis = {
            "features": {
                "shadow_area_fraction": 0.3,
                "dominant_light_direction": (0.785, 0.524),  # ~45deg az, ~30deg el
            },
            "tokens": {
                "style_key_direction": "upper_left",
            },
        }

        metadata = ShadowTokenIntegration.analysis_to_token_metadata(
            analysis, image_id="test_img"
        )

        assert metadata["light_direction"] is not None
        assert "azimuth_radians" in metadata["light_direction"]
        assert "elevation_degrees" in metadata["light_direction"]

    def test_empty_analysis(self):
        """Test handling of empty analysis."""
        analysis = {"features": {}, "tokens": {}}

        metadata = ShadowTokenIntegration.analysis_to_token_metadata(
            analysis, image_id="empty_test"
        )

        assert metadata["image_id"] == "empty_test"
        assert metadata["features"]["shadow_area_fraction"] == 0


class TestCreateShadowStyleToken:
    """Test creation of shadow style tokens."""

    def test_basic_token_creation(self):
        """Test creating a shadow style token."""
        analysis = {
            "features": {"shadow_area_fraction": 0.25},
            "tokens": {
                "style_key_direction": "overhead",
                "style_softness": "hard",
                "style_contrast": "high",
                "style_density": "moderate",
                "lighting_style": "directional",
            },
        }

        token = ShadowTokenIntegration.create_shadow_style_token(
            analysis, image_id="img_001", project_id=1
        )

        assert token["token_type"] == "shadow.lighting_style"
        assert token["style_key_direction"] == "overhead"
        assert token["style_softness"] == "hard"
        assert token["project_id"] == 1
        assert token["source_image_id"] == "img_001"

    def test_auto_semantic_name(self):
        """Test automatic semantic name generation."""
        analysis = {
            "features": {},
            "tokens": {
                "style_key_direction": "upper_left",
                "style_softness": "soft",
                "lighting_style": "diffuse",
            },
        }

        token = ShadowTokenIntegration.create_shadow_style_token(
            analysis, image_id="img", project_id=1
        )

        assert "diffuse" in token["semantic_name"]
        assert "soft" in token["semantic_name"]

    def test_custom_semantic_name(self):
        """Test custom semantic name override."""
        analysis = {"features": {}, "tokens": {}}

        token = ShadowTokenIntegration.create_shadow_style_token(
            analysis,
            image_id="img",
            project_id=1,
            semantic_name="my-custom-shadow-style",
        )

        assert token["semantic_name"] == "my-custom-shadow-style"


class TestCreateIndividualShadowTokens:
    """Test creation of individual shadow tokens."""

    def test_creates_multiple_tokens(self):
        """Test that multiple tokens are created."""
        analysis = {
            "features": {
                "shadow_area_fraction": 0.25,
                "mean_shadow_intensity": 0.3,
                "mean_lit_intensity": 0.8,
                "edge_softness_mean": 5.0,
            },
            "tokens": {
                "style_softness": "soft",
                "style_density": "moderate",
                "intensity_shadow": "medium",
                "intensity_lit": "bright",
            },
        }

        tokens = ShadowTokenIntegration.create_individual_shadow_tokens(
            analysis, image_id="img", project_id=1
        )

        assert len(tokens) >= 4  # At least intensity, light, softness, coverage
        token_types = [t["token_type"] for t in tokens]
        assert "shadow.intensity" in token_types
        assert "shadow.edge_softness" in token_types
        assert "shadow.coverage" in token_types

    def test_includes_light_direction_token(self):
        """Test that light direction token is created when available."""
        analysis = {
            "features": {
                "dominant_light_direction": (0.5, 0.3),
            },
            "tokens": {
                "style_key_direction": "left",
            },
        }

        tokens = ShadowTokenIntegration.create_individual_shadow_tokens(
            analysis, image_id="img", project_id=1
        )

        direction_tokens = [t for t in tokens if t["token_type"] == "shadow.light_direction"]
        assert len(direction_tokens) == 1
        assert "azimuth_radians" in direction_tokens[0]

    def test_token_structure(self):
        """Test that tokens have required fields."""
        analysis = {
            "features": {"shadow_area_fraction": 0.2},
            "tokens": {"style_density": "sparse"},
        }

        tokens = ShadowTokenIntegration.create_individual_shadow_tokens(
            analysis, image_id="img_123", project_id=42
        )

        for token in tokens:
            assert "token_type" in token
            assert "semantic_name" in token
            assert "source_image_id" in token
            assert token["source_image_id"] == "img_123"
            assert token["project_id"] == 42


class TestSuggestCSSBoxShadow:
    """Test CSS box-shadow generation."""

    def test_basic_css_generation(self):
        """Test basic CSS shadow generation."""
        analysis = {
            "features": {"mean_shadow_intensity": 0.3},
            "tokens": {
                "style_softness": "soft",
                "style_key_direction": "lower_right",
                "style_density": "moderate",
            },
        }

        css = ShadowTokenIntegration.suggest_css_box_shadow(analysis)

        assert "subtle" in css
        assert "medium" in css
        assert "strong" in css
        assert "rgba" in css["subtle"]

    def test_direction_affects_offset(self):
        """Test that light direction affects shadow offset."""
        analysis_left = {
            "features": {},
            "tokens": {"style_key_direction": "left", "style_softness": "medium"},
        }
        analysis_right = {
            "features": {},
            "tokens": {"style_key_direction": "right", "style_softness": "medium"},
        }

        css_left = ShadowTokenIntegration.suggest_css_box_shadow(analysis_left)
        css_right = ShadowTokenIntegration.suggest_css_box_shadow(analysis_right)

        # Left light = shadow goes right (positive x)
        # Right light = shadow goes left (negative x)
        assert css_left["direction"] == "left"
        assert css_right["direction"] == "right"

    def test_softness_affects_blur(self):
        """Test that softness affects blur radius."""
        analysis_hard = {
            "features": {},
            "tokens": {"style_softness": "hard", "style_key_direction": "overhead"},
        }
        analysis_soft = {
            "features": {},
            "tokens": {"style_softness": "very_soft", "style_key_direction": "overhead"},
        }

        css_hard = ShadowTokenIntegration.suggest_css_box_shadow(analysis_hard)
        css_soft = ShadowTokenIntegration.suggest_css_box_shadow(analysis_soft)

        assert css_hard["softness"] == "hard"
        assert css_soft["softness"] == "very_soft"


class TestValidateAnalysisForStorage:
    """Test analysis validation."""

    def test_valid_analysis(self):
        """Test validation of valid analysis."""
        analysis = {
            "features": {"shadow_area_fraction": 0.25},
            "tokens": {"extraction_confidence": 0.8},
        }

        is_valid, error = ShadowTokenIntegration.validate_analysis_for_storage(analysis)

        assert is_valid is True
        assert error is None

    def test_empty_analysis_invalid(self):
        """Test that empty analysis is invalid."""
        is_valid, error = ShadowTokenIntegration.validate_analysis_for_storage({})

        assert is_valid is False
        assert "empty" in error.lower()

    def test_missing_features_invalid(self):
        """Test that missing features dict is invalid."""
        analysis = {"tokens": {}}

        is_valid, error = ShadowTokenIntegration.validate_analysis_for_storage(analysis)

        assert is_valid is False
        assert "features" in error.lower()

    def test_low_confidence_invalid(self):
        """Test that low confidence is flagged."""
        analysis = {
            "features": {},
            "tokens": {"extraction_confidence": 0.1},
        }

        is_valid, error = ShadowTokenIntegration.validate_analysis_for_storage(
            analysis, min_confidence=0.5
        )

        assert is_valid is False
        assert "confidence" in error.lower()

    def test_nan_values_invalid(self):
        """Test that NaN values are detected."""
        analysis = {
            "features": {"shadow_area_fraction": float("nan")},
            "tokens": {"extraction_confidence": 0.8},
        }

        is_valid, error = ShadowTokenIntegration.validate_analysis_for_storage(analysis)

        assert is_valid is False
        assert "invalid" in error.lower()
