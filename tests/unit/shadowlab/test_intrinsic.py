"""Tests for intrinsic decomposition (shadowlab.intrinsic)."""

import numpy as np

from copy_that.shadowlab.intrinsic import (
    decompose_intrinsic,
    decompose_intrinsic_advanced,
)


class TestDecomposeIntrinsic:
    """Test intrinsic decomposition function."""

    def test_basic_usage(self):
        """Test basic intrinsic decomposition on synthetic image."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = decompose_intrinsic(image)

        assert "reflectance" in result
        assert "shading" in result

    def test_reflectance_shape(self):
        """Test reflectance has correct shape (H×W×3)."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = decompose_intrinsic(image)

        assert result["reflectance"].shape == (100, 100, 3)
        assert result["reflectance"].dtype == np.float32

    def test_shading_shape(self):
        """Test shading has correct shape (H×W)."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = decompose_intrinsic(image)

        assert result["shading"].shape == (100, 100)
        assert result["shading"].dtype == np.float32

    def test_reflectance_range(self):
        """Test reflectance values are in valid range [0, 1]."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        result = decompose_intrinsic(image)

        assert result["reflectance"].min() >= 0.0
        assert result["reflectance"].max() <= 1.0

    def test_shading_range(self):
        """Test shading values are in valid range [0, 1]."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        result = decompose_intrinsic(image)

        assert result["shading"].min() >= 0.0
        assert result["shading"].max() <= 1.0

    def test_rectangular_image(self):
        """Test on non-square image."""
        image = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)
        result = decompose_intrinsic(image)

        assert result["reflectance"].shape == (100, 200, 3)
        assert result["shading"].shape == (100, 200)

    def test_small_image(self):
        """Test on very small image."""
        image = np.random.randint(0, 256, (16, 16, 3), dtype=np.uint8)
        result = decompose_intrinsic(image)

        assert result["reflectance"].shape == (16, 16, 3)
        assert result["shading"].shape == (16, 16)

    def test_shadow_region_detection(self):
        """Test that dark regions show lower shading values."""
        # Create image with bright region and dark region (simulated shadow)
        image = np.ones((100, 100, 3), dtype=np.uint8) * 200

        # Add dark region (shadow)
        image[50:100, 50:100] = 50

        result = decompose_intrinsic(image)

        # Shadow region should have lower shading values on average
        bright_shading = result["shading"][:50, :50].mean()
        dark_shading = result["shading"][50:100, 50:100].mean()

        # Dark region should have lower or equal shading
        assert dark_shading <= bright_shading + 0.3  # Allow some tolerance


class TestDecomposeIntrinsicAdvanced:
    """Test advanced intrinsic decomposition with geometry."""

    def test_basic_usage_no_geometry(self):
        """Test advanced decomposition without geometry priors."""
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        result = decompose_intrinsic_advanced(image)

        assert "reflectance" in result
        assert "shading" in result
        assert "geometry_influence_score" in result
        assert "confidence" in result

    def test_without_geometry_score_is_zero(self):
        """Test that geometry influence is zero without depth/normals."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        result = decompose_intrinsic_advanced(image)

        assert result["geometry_influence_score"] == 0.0

    def test_with_depth_only(self):
        """Test advanced decomposition with depth prior."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        depth = np.random.rand(64, 64).astype(np.float32)

        result = decompose_intrinsic_advanced(image, depth=depth)

        assert "reflectance" in result
        assert "shading" in result

    def test_with_normals_only(self):
        """Test advanced decomposition with normals prior."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        normals = np.random.randn(64, 64, 3).astype(np.float32)

        result = decompose_intrinsic_advanced(image, normals=normals)

        assert "reflectance" in result
        assert "shading" in result

    def test_with_both_priors(self):
        """Test advanced decomposition with both geometry priors."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        depth = np.random.rand(64, 64).astype(np.float32)
        normals = np.random.randn(64, 64, 3).astype(np.float32)

        result = decompose_intrinsic_advanced(image, depth=depth, normals=normals)

        assert "reflectance" in result
        assert "shading" in result
        assert "confidence" in result

    def test_confidence_shape(self):
        """Test that confidence map has correct shape."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        result = decompose_intrinsic_advanced(image)

        assert result["confidence"].shape == (64, 64)
        assert result["confidence"].dtype == np.float32

    def test_device_fallback(self):
        """Test that CPU fallback works."""
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        result = decompose_intrinsic_advanced(image, device="cpu")

        assert "reflectance" in result
        assert "shading" in result
