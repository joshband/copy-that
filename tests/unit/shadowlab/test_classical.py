"""Tests for classical shadow detection (shadowlab.classical)."""

import numpy as np
import pytest

from copy_that.shadowlab.classical import ShadowClassicalConfig, detect_shadows_classical


class TestShadowClassicalConfig:
    """Test configuration dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ShadowClassicalConfig()
        assert config.brightness_percentile == 35.0
        assert config.local_window_size == 31
        assert config.morph_open_size == 3
        assert config.morph_close_size == 5

    def test_custom_config(self):
        """Test custom configuration."""
        config = ShadowClassicalConfig(
            brightness_percentile=40.0,
            local_window_size=25,
            morph_open_size=5,
        )
        assert config.brightness_percentile == 40.0
        assert config.local_window_size == 25
        assert config.morph_open_size == 5


class TestDetectShadowsClassical:
    """Test classical shadow detection."""

    def test_basic_usage(self):
        """Test basic shadow detection on synthetic image."""
        # Create synthetic image: bright background with dark square (shadow)
        height, width = 256, 256
        image = np.ones((height, width, 3), dtype=np.uint8) * 200

        # Add dark square (shadow region)
        image[60:120, 60:120] = 50

        result = detect_shadows_classical(image)

        # Check result structure
        assert "shadow_soft" in result
        assert "shadow_mask" in result
        assert "debug" in result

        # Check shapes and dtypes
        assert result["shadow_soft"].shape == (height, width)
        assert result["shadow_soft"].dtype == np.float32
        assert result["shadow_mask"].shape == (height, width)
        assert result["shadow_mask"].dtype == np.uint8

    def test_shadow_soft_range(self):
        """Test that shadow_soft is in valid range [0, 1]."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = detect_shadows_classical(image)

        shadow_soft = result["shadow_soft"]
        assert shadow_soft.min() >= 0
        assert shadow_soft.max() <= 1

    def test_shadow_mask_range(self):
        """Test that shadow_mask is binary [0, 255]."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = detect_shadows_classical(image)

        shadow_mask = result["shadow_mask"]
        assert np.all((shadow_mask == 0) | (shadow_mask == 255))

    def test_deterministic(self):
        """Test that results are deterministic for same input."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        config = ShadowClassicalConfig()

        result1 = detect_shadows_classical(image, config)
        result2 = detect_shadows_classical(image, config)

        np.testing.assert_array_equal(result1["shadow_soft"], result2["shadow_soft"])
        np.testing.assert_array_equal(result1["shadow_mask"], result2["shadow_mask"])

    def test_different_configs_give_different_results(self):
        """Test that different configs produce different results."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        config1 = ShadowClassicalConfig(brightness_percentile=30)
        config2 = ShadowClassicalConfig(brightness_percentile=50)

        result1 = detect_shadows_classical(image, config1)
        result2 = detect_shadows_classical(image, config2)

        # Results should be different (at least some pixels)
        assert not np.allclose(result1["shadow_soft"], result2["shadow_soft"])

    def test_entirely_bright_image(self):
        """Test on entirely bright image (no shadows)."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 250
        result = detect_shadows_classical(image)

        shadow_soft = result["shadow_soft"]
        shadow_mask = result["shadow_mask"]

        # Should have very little shadow
        assert shadow_soft.mean() < 0.3
        assert shadow_mask.mean() < 30  # < 12% of pixels marked as shadow

    def test_entirely_dark_image(self):
        """Test on entirely dark image (uniform darkness has no shadows)."""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 20
        result = detect_shadows_classical(image)

        shadow_soft = result["shadow_soft"]
        shadow_mask = result["shadow_mask"]

        # Entirely uniform dark image has no local contrast, so no shadow detection
        # This is correct behavior - shadows require contrast
        assert shadow_soft.mean() < 0.3
        assert shadow_mask.mean() < 50  # Few or no pixels marked as shadow

    def test_debug_info_structure(self):
        """Test that debug info has expected structure."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = detect_shadows_classical(image)

        debug = result["debug"]
        expected_keys = [
            "brightness",
            "chroma_norm",
            "local_contrast",
            "brightness_likelihood",
            "contrast_likelihood",
            "threshold_used",
            "config",
        ]

        for key in expected_keys:
            assert key in debug, f"Missing debug key: {key}"

    def test_invalid_image_raises(self):
        """Test that None or empty image raises error."""
        with pytest.raises(ValueError):
            detect_shadows_classical(None)

        with pytest.raises(ValueError):
            detect_shadows_classical(np.array([]))

    def test_large_image(self):
        """Test on larger image to ensure scalability."""
        image = np.random.randint(0, 256, (1024, 1024, 3), dtype=np.uint8)
        result = detect_shadows_classical(image)

        assert result["shadow_soft"].shape == (1024, 1024)
        assert result["shadow_mask"].shape == (1024, 1024)

    def test_small_image(self):
        """Test on very small image."""
        image = np.random.randint(0, 256, (32, 32, 3), dtype=np.uint8)
        result = detect_shadows_classical(image)

        assert result["shadow_soft"].shape == (32, 32)
        assert result["shadow_mask"].shape == (32, 32)

    def test_rectangular_image(self):
        """Test on non-square image."""
        image = np.random.randint(0, 256, (100, 300, 3), dtype=np.uint8)
        result = detect_shadows_classical(image)

        assert result["shadow_soft"].shape == (100, 300)
        assert result["shadow_mask"].shape == (100, 300)
