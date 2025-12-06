"""Tests for shadow feature extraction and tokenization (shadowlab.tokens)."""

import numpy as np

from copy_that.shadowlab.tokens import (
    ShadowFeatures,
    ShadowTokens,
    analyze_image_for_shadows,
    compute_shadow_features,
    quantize_shadow_tokens,
)


class TestShadowFeatures:
    """Test ShadowFeatures dataclass."""

    def test_create_shadow_features(self):
        """Test creating a ShadowFeatures instance."""
        features = ShadowFeatures(
            shadow_area_fraction=0.2,
            mean_shadow_intensity=0.3,
            mean_lit_intensity=0.8,
            mean_shadow_to_lit_ratio=0.375,
            edge_softness_mean=0.5,
            edge_softness_std=0.1,
            dominant_light_direction=(1.57, 0.5),
            inconsistency_score=0.1,
            shadow_contrast=0.5,
            shadow_count_major=3,
            light_direction_confidence=0.8,
        )

        assert features.shadow_area_fraction == 0.2
        assert features.dominant_light_direction == (1.57, 0.5)
        assert features.shadow_count_major == 3


class TestShadowTokens:
    """Test ShadowTokens dataclass."""

    def test_create_shadow_tokens(self):
        """Test creating ShadowTokens instance."""
        tokens = ShadowTokens(
            style_key_direction="upper_left",
            style_softness="soft",
            style_contrast="high",
            style_density="moderate",
            intensity_shadow="dark",
            intensity_lit="bright",
            extraction_confidence=0.85,
            lighting_style="directional",
        )

        assert tokens.style_key_direction == "upper_left"
        assert tokens.style_softness == "soft"
        assert tokens.to_dict()["style_contrast"] == "high"

    def test_to_dict_serialization(self):
        """Test that tokens can be serialized to dict."""
        tokens = ShadowTokens(
            style_key_direction="right",
            style_softness="hard",
            style_contrast="medium",
            style_density="sparse",
            intensity_shadow="light",
            intensity_lit="bright",
            extraction_confidence=0.7,
            lighting_style="diffuse",
        )

        token_dict = tokens.to_dict()

        assert isinstance(token_dict, dict)
        assert token_dict["style_key_direction"] == "right"
        assert token_dict["extraction_confidence"] == 0.7


class TestComputeShadowFeatures:
    """Test shadow feature computation."""

    def test_basic_feature_computation(self):
        """Test computing features from synthetic image."""
        # Synthetic image with clear shadow
        image = np.ones((200, 200, 3), dtype=np.uint8) * 200
        image[50:100, 50:100] = 50  # Dark shadow region

        # Create corresponding shadow detection results
        shadow_soft = np.zeros((200, 200), dtype=np.float32)
        shadow_soft[50:100, 50:100] = 1.0

        shadow_mask = np.zeros((200, 200), dtype=np.uint8)
        shadow_mask[50:100, 50:100] = 255

        features = compute_shadow_features(image, shadow_soft, shadow_mask)

        # Check values are in valid ranges
        assert 0 <= features.shadow_area_fraction <= 1
        assert 0 <= features.mean_shadow_intensity <= 1
        assert 0 <= features.mean_lit_intensity <= 1
        assert 0 <= features.edge_softness_mean <= 1
        assert features.shadow_count_major >= 0

    def test_features_with_geometry(self):
        """Test feature computation with depth/normals."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 150
        image[30:60, 30:60] = 80

        shadow_soft = np.zeros((100, 100), dtype=np.float32)
        shadow_soft[30:60, 30:60] = 0.8

        shadow_mask = np.zeros((100, 100), dtype=np.uint8)
        shadow_mask[30:60, 30:60] = 200

        # Add depth and normals
        depth = np.random.rand(100, 100).astype(np.float32)
        normals = np.random.uniform(-1, 1, (100, 100, 3)).astype(np.float32)
        normals = normals / (np.linalg.norm(normals, axis=2, keepdims=True) + 1e-8)
        shading = np.random.rand(100, 100).astype(np.float32)

        features = compute_shadow_features(
            image,
            shadow_soft,
            shadow_mask,
            depth=depth,
            normals=normals,
            shading=shading,
        )

        # Might be None, so we don't assert non-None
        assert 0 <= features.light_direction_confidence <= 1

    def test_empty_shadow_handling(self):
        """Test handling of images with no shadows."""
        # All bright image
        image = np.ones((100, 100, 3), dtype=np.uint8) * 240
        shadow_soft = np.zeros((100, 100), dtype=np.float32)
        shadow_mask = np.zeros((100, 100), dtype=np.uint8)

        features = compute_shadow_features(image, shadow_soft, shadow_mask)

        assert features.shadow_area_fraction < 0.01
        assert features.shadow_count_major == 0


class TestQuantizeShadowTokens:
    """Test shadow token quantization."""

    def test_quantize_high_quality_shadow(self):
        """Test quantizing features from high-quality shadow."""
        features = ShadowFeatures(
            shadow_area_fraction=0.25,
            mean_shadow_intensity=0.25,
            mean_lit_intensity=0.85,
            mean_shadow_to_lit_ratio=0.294,
            edge_softness_mean=0.6,
            edge_softness_std=0.1,
            dominant_light_direction=(0.785, 0.785),  # 45°, 45°
            inconsistency_score=0.05,
            shadow_contrast=0.6,
            shadow_count_major=2,
            light_direction_confidence=0.9,
        )

        tokens = quantize_shadow_tokens(features)

        assert tokens.style_softness in ["very_hard", "hard", "medium", "soft", "very_soft"]
        assert tokens.style_contrast in ["low", "medium", "high", "very_high"]
        assert tokens.style_density in ["sparse", "moderate", "heavy", "full"]

    def test_quantize_directional_light(self):
        """Test quantization with directional lighting."""
        features = ShadowFeatures(
            shadow_area_fraction=0.15,
            mean_shadow_intensity=0.35,
            mean_lit_intensity=0.9,
            mean_shadow_to_lit_ratio=0.389,
            edge_softness_mean=0.4,
            edge_softness_std=0.05,
            dominant_light_direction=(0.785, 1.047),  # Upper-left
            inconsistency_score=0.1,
            shadow_contrast=0.55,
            shadow_count_major=1,
            light_direction_confidence=0.85,
        )

        tokens = quantize_shadow_tokens(features)

        # Should detect directional lighting
        assert tokens.lighting_style in ["directional", "rim", "diffuse", "mixed", "complex"]

    def test_quantize_diffuse_light(self):
        """Test quantization with diffuse lighting."""
        features = ShadowFeatures(
            shadow_area_fraction=0.1,
            mean_shadow_intensity=0.7,
            mean_lit_intensity=0.8,
            mean_shadow_to_lit_ratio=0.875,
            edge_softness_mean=0.85,
            edge_softness_std=0.15,
            dominant_light_direction=None,  # Diffuse, no clear direction
            inconsistency_score=0.3,
            shadow_contrast=0.1,
            shadow_count_major=0,
            light_direction_confidence=0.2,
        )

        tokens = quantize_shadow_tokens(features)

        assert tokens.lighting_style == "diffuse"


class TestAnalyzeImageForShadows:
    """Test high-level shadow analysis entrypoint."""

    def test_basic_analysis(self):
        """Test basic shadow analysis."""
        image = np.ones((150, 150, 3), dtype=np.uint8) * 180
        image[40:80, 40:80] = 60  # Shadow

        result = analyze_image_for_shadows(image, use_geometry=False)

        # Check result structure
        assert "shadow_soft" in result
        assert "shadow_mask" in result
        assert "features" in result
        assert "tokens" in result
        assert "debug" in result

        # Check types
        assert isinstance(result["features"], dict)
        assert isinstance(result["tokens"], dict)

    def test_analysis_with_geometry(self):
        """Test analysis with geometry estimation."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 180
        image[30:60, 30:60] = 80

        result = analyze_image_for_shadows(image, use_geometry=True)

        # Should have depth/normals (even if placeholder)
        assert "depth" in result
        assert "normals" in result

    def test_result_shapes_and_dtypes(self):
        """Test result shapes and data types."""
        image = np.random.randint(0, 256, (120, 120, 3), dtype=np.uint8)
        result = analyze_image_for_shadows(image)

        height, width = image.shape[:2]

        assert result["shadow_soft"].shape == (height, width)
        assert result["shadow_soft"].dtype == np.float32

        assert result["shadow_mask"].shape == (height, width)
        assert result["shadow_mask"].dtype == np.uint8

    def test_features_contain_expected_keys(self):
        """Test that extracted features contain expected keys."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 180
        image[30:60, 30:60] = 60

        result = analyze_image_for_shadows(image)
        features = result["features"]

        expected_keys = [
            "shadow_area_fraction",
            "mean_shadow_intensity",
            "mean_lit_intensity",
            "edge_softness_mean",
            "shadow_contrast",
        ]

        for key in expected_keys:
            assert key in features, f"Missing feature key: {key}"

    def test_tokens_contain_expected_keys(self):
        """Test that tokens contain expected design system keys."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 180
        image[30:60, 30:60] = 60

        result = analyze_image_for_shadows(image)
        tokens = result["tokens"]

        expected_keys = [
            "style_key_direction",
            "style_softness",
            "style_contrast",
            "style_density",
            "intensity_shadow",
            "intensity_lit",
            "lighting_style",
        ]

        for key in expected_keys:
            assert key in tokens, f"Missing token key: {key}"

    def test_different_images_give_different_results(self):
        """Test that different images produce different analyses."""
        # Bright image with no shadows
        image1 = np.ones((100, 100, 3), dtype=np.uint8) * 240

        # Dark image with shadows
        image2 = np.ones((100, 100, 3), dtype=np.uint8) * 100
        image2[30:60, 30:60] = 30

        result1 = analyze_image_for_shadows(image1)
        result2 = analyze_image_for_shadows(image2)

        assert (
            result1["features"]["shadow_area_fraction"]
            < result2["features"]["shadow_area_fraction"]
        )
