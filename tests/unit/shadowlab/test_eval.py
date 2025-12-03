"""Tests for shadow evaluation metrics (shadowlab.eval)."""

import numpy as np

from copy_that.shadowlab.eval import (
    ShadowEvaluationMetrics,
    compare_shadow_masks,
    evaluate_multi_method_comparison,
)


class TestShadowEvaluationMetrics:
    """Test evaluation metrics dataclass."""

    def test_create_metrics(self):
        """Test creating metrics instance."""
        metrics = ShadowEvaluationMetrics(
            iou=0.75,
            precision=0.8,
            recall=0.7,
            f1=0.75,
            mae=0.1,
        )

        assert metrics.iou == 0.75
        assert metrics.f1 == 0.75

    def test_metrics_str_representation(self):
        """Test string representation of metrics."""
        metrics = ShadowEvaluationMetrics(
            iou=0.75,
            precision=0.8,
            recall=0.7,
            f1=0.75,
            mae=0.1,
        )

        str_repr = str(metrics)
        assert "IoU" in str_repr
        assert "Precision" in str_repr


class TestCompareShadowMasks:
    """Test shadow mask comparison and evaluation."""

    def test_perfect_prediction(self):
        """Test with perfect prediction (identical masks)."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 255

        metrics = compare_shadow_masks(mask, mask)

        assert metrics.iou == 1.0
        assert metrics.precision == 1.0
        assert metrics.recall == 1.0
        assert np.isclose(metrics.f1, 1.0)  # Allow for floating point precision
        assert metrics.mae == 0.0

    def test_completely_wrong_prediction(self):
        """Test with completely wrong prediction."""
        gt = np.zeros((100, 100), dtype=np.uint8)
        gt[30:70, 30:70] = 255

        pred = np.zeros((100, 100), dtype=np.uint8)
        pred[0:40, 0:40] = 255

        metrics = compare_shadow_masks(pred, gt)

        # Should have low scores
        assert metrics.iou < 0.5
        assert metrics.f1 < 0.5

    def test_partial_overlap(self):
        """Test with partial overlap between masks."""
        gt = np.zeros((100, 100), dtype=np.uint8)
        gt[30:70, 30:70] = 255

        pred = np.zeros((100, 100), dtype=np.uint8)
        pred[50:90, 50:90] = 255

        metrics = compare_shadow_masks(pred, gt)

        # Should have intermediate scores
        assert 0 < metrics.iou < 1
        assert 0 < metrics.f1 < 1
        assert metrics.precision > 0
        assert metrics.recall > 0

    def test_all_metrics_in_range(self):
        """Test that all metrics are in valid ranges."""
        gt = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        pred = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        metrics = compare_shadow_masks(pred, gt)

        assert 0 <= metrics.iou <= 1
        assert 0 <= metrics.precision <= 1
        assert 0 <= metrics.recall <= 1
        assert 0 <= metrics.f1 <= 1
        assert 0 <= metrics.mae <= 1

    def test_float_masks_are_binarized(self):
        """Test that float masks are properly binarized."""
        # For float masks, values are typically 0..1, not 0..255
        # Need to scale them up or the binarization won't work correctly
        gt = np.zeros((100, 100), dtype=np.float32)
        gt[30:70, 30:70] = 255.0  # Convert to uint8 range

        pred = np.zeros((100, 100), dtype=np.float32)
        pred[30:70, 30:70] = 240.0  # Slightly different in uint8 range

        metrics = compare_shadow_masks(pred, gt)

        # Should be treated as identical after binarization (both > 127)
        assert metrics.iou == 1.0

    def test_empty_masks(self):
        """Test with empty masks (no shadow)."""
        gt = np.zeros((100, 100), dtype=np.uint8)
        pred = np.zeros((100, 100), dtype=np.uint8)

        metrics = compare_shadow_masks(pred, gt)

        # Empty masks should match perfectly (no FP, no FN)
        # IoU = 0/0 which we handle as 1.0
        assert metrics.mae == 0.0

    def test_false_positives(self):
        """Test scenario with false positives."""
        gt = np.zeros((100, 100), dtype=np.uint8)
        gt[30:70, 30:70] = 255

        pred = np.zeros((100, 100), dtype=np.uint8)
        pred[30:70, 30:70] = 255
        pred[10:30, 10:30] = 255  # Extra shadow (FP)

        metrics = compare_shadow_masks(pred, gt)

        # Precision < Recall (FP makes precision lower)
        assert metrics.precision < metrics.recall
        assert metrics.precision < 1.0

    def test_false_negatives(self):
        """Test scenario with false negatives."""
        gt = np.zeros((100, 100), dtype=np.uint8)
        gt[30:70, 30:70] = 255
        gt[10:30, 10:30] = 255

        pred = np.zeros((100, 100), dtype=np.uint8)
        pred[30:70, 30:70] = 255  # Missing one shadow

        metrics = compare_shadow_masks(pred, gt)

        # Recall < Precision (FN makes recall lower)
        assert metrics.recall < metrics.precision
        assert metrics.recall < 1.0

    def test_large_masks(self):
        """Test with large mask arrays."""
        gt = np.random.randint(0, 256, (1024, 1024), dtype=np.uint8)
        pred = np.random.randint(0, 256, (1024, 1024), dtype=np.uint8)

        metrics = compare_shadow_masks(pred, gt)

        # Should still produce valid metrics
        assert 0 <= metrics.iou <= 1
        assert 0 <= metrics.f1 <= 1

    def test_rectangular_masks(self):
        """Test with non-square masks."""
        gt = np.random.randint(0, 256, (200, 300), dtype=np.uint8)
        pred = np.random.randint(0, 256, (200, 300), dtype=np.uint8)

        metrics = compare_shadow_masks(pred, gt)

        # Should handle rectangular shapes
        assert 0 <= metrics.iou <= 1


class TestEvaluateMultiMethodComparison:
    """Test multi-method comparison utility."""

    def test_basic_comparison(self):
        """Test comparing multiple methods."""
        gt = np.zeros((100, 100), dtype=np.uint8)
        gt[30:70, 30:70] = 255

        # Create predictions from different methods
        pred_cv = np.zeros((100, 100), dtype=np.uint8)
        pred_cv[25:75, 25:75] = 255  # Good but slightly offset

        pred_ai = np.zeros((100, 100), dtype=np.uint8)
        pred_ai[30:70, 30:70] = 255  # Perfect

        results = evaluate_multi_method_comparison(
            gt,
            {
                "CV": pred_cv,
                "AI": pred_ai,
            },
        )

        # Should have results for both methods
        assert "CV" in results
        assert "AI" in results

        # AI should have better metrics
        assert results["AI"].iou >= results["CV"].iou
        assert results["AI"].f1 >= results["CV"].f1

    def test_comparison_with_single_method(self):
        """Test comparison with only one method."""
        gt = np.zeros((100, 100), dtype=np.uint8)
        gt[30:70, 30:70] = 255

        pred = np.zeros((100, 100), dtype=np.uint8)
        pred[30:70, 30:70] = 255

        results = evaluate_multi_method_comparison(gt, {"Perfect": pred})

        assert len(results) == 1
        assert results["Perfect"].iou == 1.0

    def test_comparison_with_many_methods(self):
        """Test comparison with many methods."""
        gt = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        methods = {
            f"method_{i}": np.random.randint(0, 256, (100, 100), dtype=np.uint8) for i in range(10)
        }

        results = evaluate_multi_method_comparison(gt, methods)

        assert len(results) == 10
        for metrics in results.values():
            assert isinstance(metrics, ShadowEvaluationMetrics)
            assert 0 <= metrics.iou <= 1
            assert 0 <= metrics.f1 <= 1

    def test_comparison_all_metrics_valid(self):
        """Test that all returned metrics are valid."""
        gt = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        pred1 = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        pred2 = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        results = evaluate_multi_method_comparison(
            gt,
            {
                "method_1": pred1,
                "method_2": pred2,
            },
        )

        for method_name, metrics in results.items():
            assert isinstance(metrics, ShadowEvaluationMetrics)
            assert 0 <= metrics.iou <= 1
            assert 0 <= metrics.precision <= 1
            assert 0 <= metrics.recall <= 1
            assert 0 <= metrics.f1 <= 1
            assert 0 <= metrics.mae <= 1
