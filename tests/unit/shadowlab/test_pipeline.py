"""Tests for shadow extraction pipeline (shadowlab.pipeline).

Tests for stages 01-03 (Input, Illumination, Classical) and stage 06 (MiDaS Depth).
"""

import numpy as np
import pytest

from copy_that.shadowlab.pipeline import (
    illumination_invariant_v,
    classical_shadow_candidates,
    depth_to_normals,
    light_dir_to_angles,
    run_midas_depth,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def random_rgb_image() -> np.ndarray:
    """Create a random RGB image in float32 [0, 1] range."""
    np.random.seed(42)
    return np.random.rand(256, 256, 3).astype(np.float32)


@pytest.fixture
def synthetic_shadow_image() -> np.ndarray:
    """Create an image with a clear shadow region (dark area on bright background)."""
    image = np.ones((256, 256, 3), dtype=np.float32) * 0.8
    # Add dark shadow region
    image[80:160, 80:180] = 0.2
    return image


@pytest.fixture
def illumination_map(synthetic_shadow_image: np.ndarray) -> np.ndarray:
    """Pre-computed illumination map for tests."""
    return illumination_invariant_v(synthetic_shadow_image)


@pytest.fixture
def synthetic_depth_map() -> np.ndarray:
    """Create a synthetic depth map with gradient."""
    h, w = 256, 256
    # Create depth gradient (closer at bottom, farther at top)
    y_gradient = np.linspace(0, 1, h)[:, np.newaxis]
    depth = np.broadcast_to(y_gradient, (h, w)).astype(np.float32).copy()
    return depth


# ============================================================================
# Stage 02: Illumination Invariant Tests
# ============================================================================


class TestIlluminationInvariantV:
    """Test illumination invariant brightness computation."""

    def test_output_shape(self, random_rgb_image: np.ndarray):
        """Test output has correct shape (H, W)."""
        result = illumination_invariant_v(random_rgb_image)
        h, w = random_rgb_image.shape[:2]
        assert result.shape == (h, w)

    def test_output_dtype(self, random_rgb_image: np.ndarray):
        """Test output is float32."""
        result = illumination_invariant_v(random_rgb_image)
        assert result.dtype == np.float32

    def test_output_range(self, random_rgb_image: np.ndarray):
        """Test output values are in [0, 1] range."""
        result = illumination_invariant_v(random_rgb_image)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_dark_regions_have_low_values(self, synthetic_shadow_image: np.ndarray):
        """Test that dark regions in image have lower illumination values."""
        result = illumination_invariant_v(synthetic_shadow_image)
        # Shadow region is at [80:160, 80:180]
        shadow_mean = result[80:160, 80:180].mean()
        # Background is outside shadow
        background_mean = result[0:50, 0:50].mean()
        assert shadow_mean < background_mean

    def test_uniform_image(self):
        """Test on uniform (constant) image."""
        uniform = np.ones((64, 64, 3), dtype=np.float32) * 0.5
        result = illumination_invariant_v(uniform)
        assert result.shape == (64, 64)
        assert result.dtype == np.float32

    def test_black_image(self):
        """Test on pure black image."""
        black = np.zeros((64, 64, 3), dtype=np.float32)
        result = illumination_invariant_v(black)
        # Should handle gracefully without division errors
        assert result.shape == (64, 64)
        assert not np.any(np.isnan(result))

    def test_white_image(self):
        """Test on pure white image."""
        white = np.ones((64, 64, 3), dtype=np.float32)
        result = illumination_invariant_v(white)
        assert result.shape == (64, 64)
        assert not np.any(np.isnan(result))


# ============================================================================
# Stage 03: Classical Shadow Candidates Tests
# ============================================================================


class TestClassicalShadowCandidates:
    """Test classical shadow candidate detection."""

    def test_output_shape(self, illumination_map: np.ndarray):
        """Test output has correct shape."""
        result = classical_shadow_candidates(illumination_map)
        assert result.shape == illumination_map.shape

    def test_output_dtype(self, illumination_map: np.ndarray):
        """Test output is float32."""
        result = classical_shadow_candidates(illumination_map)
        assert result.dtype == np.float32

    def test_output_range(self, illumination_map: np.ndarray):
        """Test output values are in [0, 1] range."""
        result = classical_shadow_candidates(illumination_map)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_detects_dark_regions(self, synthetic_shadow_image: np.ndarray):
        """Test that dark regions are detected as shadow candidates."""
        illum = illumination_invariant_v(synthetic_shadow_image)
        result = classical_shadow_candidates(illum)
        # Shadow region at [80:160, 80:180] should have higher candidate values
        shadow_mean = result[90:150, 90:170].mean()
        background_mean = result[0:40, 0:40].mean()
        # Shadow region should have higher candidate probability
        assert shadow_mean > background_mean

    def test_custom_threshold(self, illumination_map: np.ndarray):
        """Test with custom threshold percentile."""
        result_low = classical_shadow_candidates(illumination_map, threshold_percentile=10.0)
        result_high = classical_shadow_candidates(illumination_map, threshold_percentile=50.0)
        # Higher threshold should detect more shadow candidates
        assert result_high.mean() >= result_low.mean()

    def test_min_area_filtering(self, illumination_map: np.ndarray):
        """Test that small regions are filtered out."""
        result_small = classical_shadow_candidates(illumination_map, min_area=1)
        result_large = classical_shadow_candidates(illumination_map, min_area=100)
        # Larger min_area should result in fewer/smaller shadow regions
        assert result_large.sum() <= result_small.sum()


# ============================================================================
# Stage 06: MiDaS Depth Estimation Tests
# ============================================================================


class TestRunMidasDepth:
    """Test MiDaS depth estimation (or fallback)."""

    def test_output_shape(self, random_rgb_image: np.ndarray):
        """Test output has correct shape."""
        result = run_midas_depth(random_rgb_image)
        h, w = random_rgb_image.shape[:2]
        assert result.shape == (h, w)

    def test_output_dtype(self, random_rgb_image: np.ndarray):
        """Test output is float32."""
        result = run_midas_depth(random_rgb_image)
        assert result.dtype == np.float32

    def test_output_range(self, random_rgb_image: np.ndarray):
        """Test output values are normalized to [0, 1] range."""
        result = run_midas_depth(random_rgb_image)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_handles_different_sizes(self):
        """Test depth estimation works for various image sizes."""
        for size in [(64, 64), (128, 256), (300, 200)]:
            h, w = size
            image = np.random.rand(h, w, 3).astype(np.float32)
            result = run_midas_depth(image)
            assert result.shape == (h, w)

    def test_no_nan_values(self, random_rgb_image: np.ndarray):
        """Test output contains no NaN values."""
        result = run_midas_depth(random_rgb_image)
        assert not np.any(np.isnan(result))


class TestDepthToNormals:
    """Test depth to normals conversion.

    Note: depth_to_normals returns (normals, normals_vis) tuple.
    """

    def test_returns_tuple(self, synthetic_depth_map: np.ndarray):
        """Test returns (normals, normals_vis) tuple."""
        result = depth_to_normals(synthetic_depth_map)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_normals_output_shape(self, synthetic_depth_map: np.ndarray):
        """Test normals output has correct shape (H, W, 3)."""
        normals, normals_vis = depth_to_normals(synthetic_depth_map)
        h, w = synthetic_depth_map.shape
        assert normals.shape == (h, w, 3)
        assert normals_vis.shape == (h, w, 3)

    def test_normals_output_dtype(self, synthetic_depth_map: np.ndarray):
        """Test normals output is float32."""
        normals, normals_vis = depth_to_normals(synthetic_depth_map)
        assert normals.dtype == np.float32
        assert normals_vis.dtype == np.float32

    def test_normals_vis_range(self, synthetic_depth_map: np.ndarray):
        """Test normals_vis is in [0, 1] for visualization."""
        normals, normals_vis = depth_to_normals(synthetic_depth_map)
        assert normals_vis.min() >= 0.0
        assert normals_vis.max() <= 1.0


# ============================================================================
# Lighting Utilities Tests
# ============================================================================


class TestLightDirToAngles:
    """Test light direction to angles conversion."""

    def test_basic_directions(self):
        """Test known light directions produce expected angles."""
        # Light from above (negative Y in screen coords)
        direction = np.array([0.0, -1.0, 0.0])
        azimuth, elevation = light_dir_to_angles(direction)
        assert isinstance(azimuth, float)
        assert isinstance(elevation, float)

    def test_angle_ranges(self):
        """Test angles are in expected ranges."""
        # Random direction
        direction = np.array([0.5, -0.5, 0.707])
        direction = direction / np.linalg.norm(direction)
        azimuth, elevation = light_dir_to_angles(direction)
        # Azimuth should be in [0, 360] or [-180, 180]
        assert -360 <= azimuth <= 360
        # Elevation should be in [-90, 90]
        assert -90 <= elevation <= 90


# ============================================================================
# Integration Test
# ============================================================================


class TestPipelineFunctionsIntegration:
    """Test that pipeline functions work together."""

    def test_illumination_to_candidates_chain(self, synthetic_shadow_image: np.ndarray):
        """Test illumination output can be used as candidates input."""
        illum = illumination_invariant_v(synthetic_shadow_image)
        candidates = classical_shadow_candidates(illum)

        assert candidates.shape == illum.shape
        assert candidates.dtype == np.float32

    def test_depth_to_normals_chain(self, random_rgb_image: np.ndarray):
        """Test depth estimation output can be used for normals."""
        depth = run_midas_depth(random_rgb_image)
        normals, normals_vis = depth_to_normals(depth)

        h, w = random_rgb_image.shape[:2]
        assert normals.shape == (h, w, 3)
        assert normals_vis.shape == (h, w, 3)
