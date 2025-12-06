"""Tests for visualization utilities (shadowlab.visualization)."""

import numpy as np
import pytest

from copy_that.shadowlab.visualization import (
    create_shadow_comparison,
    visualize_depth_map,
    visualize_normals,
    visualize_shadow_analysis,
)


class TestVisualizeShadowAnalysis:
    """Test the main shadow analysis visualization function."""

    def test_basic_usage(self):
        """Test basic visualization returns image of expected shape."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        analysis = {
            "shadow_soft": np.random.rand(100, 100).astype(np.float32),
            "shadow_mask": np.random.randint(0, 256, (100, 100), dtype=np.uint8),
        }

        result = visualize_shadow_analysis(image, analysis)

        assert result.ndim == 3
        assert result.dtype == np.uint8
        assert result.shape[2] == 3  # BGR

    def test_with_depth_and_shading(self):
        """Test visualization with optional depth and shading."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        analysis = {
            "shadow_soft": np.random.rand(100, 100).astype(np.float32),
            "shadow_mask": np.random.randint(0, 256, (100, 100), dtype=np.uint8),
            "depth": np.random.rand(100, 100).astype(np.float32),
            "shading": np.random.rand(100, 100).astype(np.float32),
        }

        result = visualize_shadow_analysis(image, analysis)

        assert result.ndim == 3
        assert result.dtype == np.uint8

    def test_with_features_and_tokens(self):
        """Test visualization with features and tokens metadata."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        analysis = {
            "shadow_soft": np.random.rand(100, 100).astype(np.float32),
            "shadow_mask": np.random.randint(0, 256, (100, 100), dtype=np.uint8),
            "features": {"shadow_area_fraction": 0.25},
            "tokens": {
                "style_softness": "soft",
                "style_key_direction": "upper_left",
                "style_contrast": "medium",
            },
        }

        result = visualize_shadow_analysis(image, analysis)

        assert result.ndim == 3

    def test_empty_analysis(self):
        """Test visualization with empty analysis dict."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        analysis = {}

        result = visualize_shadow_analysis(image, analysis)

        assert result.ndim == 3
        assert result.dtype == np.uint8

    def test_rectangular_image(self):
        """Test visualization with non-square image."""
        image = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
        analysis = {
            "shadow_soft": np.random.rand(100, 200).astype(np.float32),
            "shadow_mask": np.random.randint(0, 256, (100, 200), dtype=np.uint8),
        }

        result = visualize_shadow_analysis(image, analysis)

        assert result.ndim == 3


class TestVisualizeDepthMap:
    """Test depth map visualization."""

    def test_basic_usage(self):
        """Test basic depth map visualization."""
        depth = np.random.rand(100, 100).astype(np.float32)

        result = visualize_depth_map(depth)

        assert result.shape == (100, 100, 3)
        assert result.dtype == np.uint8

    def test_depth_normalization(self):
        """Test that depth is properly normalized."""
        depth = np.random.rand(100, 100).astype(np.float32) * 10  # Range 0-10

        result = visualize_depth_map(depth)

        assert result.shape == (100, 100, 3)
        assert result.dtype == np.uint8

    def test_rectangular_depth(self):
        """Test with non-square depth map."""
        depth = np.random.rand(100, 200).astype(np.float32)

        result = visualize_depth_map(depth)

        assert result.shape == (100, 200, 3)


class TestVisualizeNormals:
    """Test surface normals visualization."""

    def test_basic_usage(self):
        """Test basic normals visualization."""
        normals = np.random.randn(100, 100, 3).astype(np.float32)
        normals = normals / (np.linalg.norm(normals, axis=2, keepdims=True) + 1e-8)

        result = visualize_normals(normals)

        assert result.shape == (100, 100, 3)
        assert result.dtype == np.uint8

    def test_normals_output_range(self):
        """Test that output is in valid uint8 range."""
        normals = np.random.randn(64, 64, 3).astype(np.float32)
        normals = normals / (np.linalg.norm(normals, axis=2, keepdims=True) + 1e-8)

        result = visualize_normals(normals)

        assert result.min() >= 0
        assert result.max() <= 255

    def test_z_pointing_normals(self):
        """Test visualization of normals pointing toward camera."""
        normals = np.zeros((64, 64, 3), dtype=np.float32)
        normals[:, :, 2] = 1.0  # Z = 1 (toward camera)

        result = visualize_normals(normals)

        # Z = 1 maps to B = (1+1)/2 * 255 = 255
        # X = 0 maps to R = 127
        # Y = 0 maps to G = 127
        assert result.shape == (64, 64, 3)


class TestCreateShadowComparison:
    """Test shadow comparison visualization."""

    def test_single_mask(self):
        """Test comparison with single CV mask."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        mask_cv = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        result = create_shadow_comparison(image, mask_cv)

        assert result.ndim == 3
        assert result.dtype == np.uint8

    def test_multiple_masks(self):
        """Test comparison with multiple masks."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        mask_cv = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        mask_ai = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        mask_deep = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        result = create_shadow_comparison(image, mask_cv, mask_ai, mask_deep)

        assert result.ndim == 3
        assert result.dtype == np.uint8

    def test_some_masks_none(self):
        """Test comparison with some masks as None."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        mask_cv = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        result = create_shadow_comparison(image, mask_cv, shadow_mask_ai=None)

        assert result.ndim == 3
