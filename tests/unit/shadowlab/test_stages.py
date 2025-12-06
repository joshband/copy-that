"""Tests for shadow pipeline stage functions (shadowlab.stages).

Tests for stage wrapper functions that produce ShadowStageResult, layers, and artifacts.
"""

import numpy as np
import pytest

from copy_that.shadowlab.pipeline import ShadowStageResult, ShadowVisualLayer
from copy_that.shadowlab.stages import (
    stage_02_illumination,
    stage_03_candidates,
    stage_06_geometry,
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
    """Pre-computed illumination map from stage_02."""
    from copy_that.shadowlab.pipeline import illumination_invariant_v

    return illumination_invariant_v(synthetic_shadow_image)


# ============================================================================
# Stage 02: Illumination Tests
# ============================================================================


class TestStage02Illumination:
    """Test stage 02 illumination invariant computation."""

    def test_returns_tuple(self, random_rgb_image: np.ndarray):
        """Test returns (ShadowStageResult, layers, artifacts) tuple."""
        result = stage_02_illumination(random_rgb_image)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_stage_result_structure(self, random_rgb_image: np.ndarray):
        """Test ShadowStageResult has correct ID and metrics."""
        stage, layers, artifacts = stage_02_illumination(random_rgb_image)

        assert isinstance(stage, ShadowStageResult)
        assert stage.id == "shadow_stage_02_invariant"
        assert stage.duration_ms >= 0
        # Should have metrics about illumination
        assert isinstance(stage.metrics, dict)

    def test_artifacts_contains_illumination_map(self, random_rgb_image: np.ndarray):
        """Test artifacts contains illumination map."""
        stage, layers, artifacts = stage_02_illumination(random_rgb_image)

        assert "illumination_map" in artifacts
        illum = artifacts["illumination_map"]
        h, w = random_rgb_image.shape[:2]
        assert illum.shape == (h, w)
        assert illum.dtype == np.float32

    def test_has_visual_layer(self, random_rgb_image: np.ndarray):
        """Test stage produces visual layer for illumination map."""
        stage, layers, artifacts = stage_02_illumination(random_rgb_image)

        assert len(layers) >= 1
        # At least one layer should reference illumination
        layer_ids = [layer.id for layer in layers]
        assert any("illumination" in lid or "invariant" in lid for lid in layer_ids)


# ============================================================================
# Stage 03: Classical Candidates Tests
# ============================================================================


class TestStage03Candidates:
    """Test stage 03 classical shadow candidate detection."""

    def test_returns_tuple(self, illumination_map: np.ndarray):
        """Test returns (ShadowStageResult, layers, artifacts) tuple."""
        result = stage_03_candidates(illumination_map)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_stage_result_structure(self, illumination_map: np.ndarray):
        """Test ShadowStageResult has correct ID and metrics."""
        stage, layers, artifacts = stage_03_candidates(illumination_map)

        assert isinstance(stage, ShadowStageResult)
        assert stage.id == "shadow_stage_03_candidates"
        assert stage.duration_ms >= 0
        # Should have coverage metric
        assert "candidate_coverage" in stage.metrics

    def test_coverage_metric_range(self, illumination_map: np.ndarray):
        """Test coverage metric is in valid range."""
        stage, layers, artifacts = stage_03_candidates(illumination_map)

        coverage = stage.metrics["candidate_coverage"]
        assert 0.0 <= coverage <= 1.0

    def test_artifacts_contains_candidate_mask(self, illumination_map: np.ndarray):
        """Test artifacts contains candidate mask."""
        stage, layers, artifacts = stage_03_candidates(illumination_map)

        assert "candidate_mask" in artifacts
        mask = artifacts["candidate_mask"]
        assert mask.shape == illumination_map.shape
        assert mask.dtype == np.float32

    def test_has_visual_layer(self, illumination_map: np.ndarray):
        """Test stage produces visual layer for candidates."""
        stage, layers, artifacts = stage_03_candidates(illumination_map)

        assert len(layers) >= 1


# ============================================================================
# Stage 06: Depth Tests
# ============================================================================


class TestStage06Geometry:
    """Test stage 06 depth and normals estimation."""

    def test_returns_tuple(self, random_rgb_image: np.ndarray):
        """Test returns (ShadowStageResult, layers, artifacts) tuple."""
        result = stage_06_geometry(random_rgb_image)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_stage_result_structure(self, random_rgb_image: np.ndarray):
        """Test ShadowStageResult has correct ID."""
        stage, layers, artifacts = stage_06_geometry(random_rgb_image)

        assert isinstance(stage, ShadowStageResult)
        assert stage.id == "shadow_stage_06_geometry"
        assert stage.duration_ms >= 0

    def test_artifacts_contains_depth_map(self, random_rgb_image: np.ndarray):
        """Test artifacts contains depth map."""
        stage, layers, artifacts = stage_06_geometry(random_rgb_image)

        assert "depth_map" in artifacts
        depth = artifacts["depth_map"]
        h, w = random_rgb_image.shape[:2]
        assert depth.shape == (h, w)
        assert depth.dtype == np.float32

    def test_artifacts_contains_normals(self, random_rgb_image: np.ndarray):
        """Test artifacts contains normal map."""
        stage, layers, artifacts = stage_06_geometry(random_rgb_image)

        assert "normal_map" in artifacts
        normals = artifacts["normal_map"]
        h, w = random_rgb_image.shape[:2]
        assert normals.shape == (h, w, 3)
        assert normals.dtype == np.float32

    def test_depth_in_valid_range(self, random_rgb_image: np.ndarray):
        """Test depth values are in [0, 1] range."""
        stage, layers, artifacts = stage_06_geometry(random_rgb_image)

        depth = artifacts["depth_map"]
        assert depth.min() >= 0.0
        assert depth.max() <= 1.0

    def test_has_visual_layers(self, random_rgb_image: np.ndarray):
        """Test stage produces visual layers for depth and normals."""
        stage, layers, artifacts = stage_06_geometry(random_rgb_image)

        # Should have at least depth and normal layers
        assert len(layers) >= 2


# ============================================================================
# Stage Integration Tests
# ============================================================================


class TestStageChaining:
    """Test that stages can be chained together."""

    def test_stage_02_to_03(self, synthetic_shadow_image: np.ndarray):
        """Test stage 02 output feeds into stage 03."""
        stage2, layers2, artifacts2 = stage_02_illumination(synthetic_shadow_image)
        illum = artifacts2["illumination_map"]

        stage3, layers3, artifacts3 = stage_03_candidates(illum)
        assert "candidate_mask" in artifacts3

    def test_full_chain_02_to_03(self, synthetic_shadow_image: np.ndarray):
        """Test complete chain from stage 02 to 03."""
        # Stage 02
        stage2, _, artifacts2 = stage_02_illumination(synthetic_shadow_image)
        assert stage2.id == "shadow_stage_02_invariant"

        # Stage 03
        stage3, _, artifacts3 = stage_03_candidates(artifacts2["illumination_map"])
        assert stage3.id == "shadow_stage_03_candidates"

        # Verify final output
        assert "candidate_mask" in artifacts3
        assert artifacts3["candidate_mask"].shape == synthetic_shadow_image.shape[:2]

    def test_stage_narratives_exist(self, random_rgb_image: np.ndarray):
        """Test stages have narrative descriptions."""
        stage2, _, _ = stage_02_illumination(random_rgb_image)

        assert stage2.stage_narrative
        assert len(stage2.stage_narrative) > 10  # Not empty

    def test_stage_06_independent(self, random_rgb_image: np.ndarray):
        """Test stage 06 can run independently on RGB."""
        stage6, layers6, artifacts6 = stage_06_geometry(random_rgb_image)

        assert stage6.id == "shadow_stage_06_geometry"
        assert "depth_map" in artifacts6
        assert "normal_map" in artifacts6
