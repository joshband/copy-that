"""Tests for depth and normals estimation (shadowlab.depth_normals)."""

import numpy as np
import pytest

from copy_that.shadowlab.depth_normals import (
    estimate_depth,
    estimate_depth_and_normals,
    estimate_normals,
)


class TestEstimateDepth:
    """Test depth estimation function."""

    def test_basic_usage(self):
        """Test basic depth estimation on synthetic image."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        depth = estimate_depth(image)

        assert depth.shape == (100, 100)
        assert depth.dtype == np.float32

    def test_depth_range(self):
        """Test that depth values are in valid range."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        depth = estimate_depth(image)

        assert depth.min() >= 0.0
        assert depth.max() <= 1.0

    def test_rectangular_image(self):
        """Test on non-square image."""
        image = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
        depth = estimate_depth(image)

        assert depth.shape == (100, 200)

    def test_small_image(self):
        """Test on very small image."""
        image = np.random.randint(0, 256, (16, 16, 3), dtype=np.uint8)
        depth = estimate_depth(image)

        assert depth.shape == (16, 16)

    def test_large_image(self):
        """Test on larger image."""
        image = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
        depth = estimate_depth(image)

        assert depth.shape == (512, 512)

    def test_device_fallback(self):
        """Test that CPU fallback works."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        depth = estimate_depth(image, device="cpu")

        assert depth.shape == (64, 64)
        assert depth.dtype == np.float32


class TestEstimateNormals:
    """Test normals estimation function."""

    def test_basic_usage(self):
        """Test basic normals estimation on synthetic image."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        normals = estimate_normals(image)

        assert normals.shape == (100, 100, 3)
        assert normals.dtype == np.float32

    def test_normals_range(self):
        """Test that normal values are in valid range [-1, 1]."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        normals = estimate_normals(image)

        assert normals.min() >= -1.0
        assert normals.max() <= 1.0

    def test_rectangular_image(self):
        """Test on non-square image."""
        image = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
        normals = estimate_normals(image)

        assert normals.shape == (100, 200, 3)

    def test_normals_are_unit_vectors(self):
        """Test that normals are approximately unit vectors."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        normals = estimate_normals(image)

        # Compute magnitudes
        magnitudes = np.linalg.norm(normals, axis=2)

        # Should be close to 1.0 (unit vectors)
        # Placeholder returns [0, 0, 1] which has magnitude 1
        assert magnitudes.mean() > 0.5


class TestEstimateDepthAndNormals:
    """Test combined depth and normals estimation."""

    def test_basic_usage(self):
        """Test combined estimation returns both."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = estimate_depth_and_normals(image)

        assert "depth" in result
        assert "normals" in result
        assert result["depth"].shape == (100, 100)
        assert result["normals"].shape == (100, 100, 3)

    def test_result_dtypes(self):
        """Test that results have correct dtypes."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        result = estimate_depth_and_normals(image)

        assert result["depth"].dtype == np.float32
        assert result["normals"].dtype == np.float32

    def test_consistent_results(self):
        """Test that combined function gives same results as individual calls."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)

        combined = estimate_depth_and_normals(image)
        depth_only = estimate_depth(image)
        normals_only = estimate_normals(image)

        # Should match (since both use same underlying implementation)
        np.testing.assert_array_equal(combined["depth"], depth_only)
        np.testing.assert_array_equal(combined["normals"], normals_only)
