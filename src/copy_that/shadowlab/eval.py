"""
Evaluation metrics for shadow detection quality.

Provides standard metrics for comparing predicted and ground-truth shadow masks:
- IoU (Intersection over Union)
- Precision, Recall, F1
- MAE (Mean Absolute Error)
- Boundary Recall

These metrics are useful for:
- Validating detection algorithms
- Comparing different approaches
- Tuning hyperparameters
- Benchmarking against datasets (ISTD, SBU, UOLED, etc.)
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class ShadowEvaluationMetrics:
    """Shadow mask evaluation results."""

    iou: float
    """Intersection over Union (Jaccard index), 0..1."""

    precision: float
    """True Positives / (TP + FP), 0..1."""

    recall: float
    """True Positives / (TP + FN), 0..1."""

    f1: float
    """Harmonic mean of precision and recall, 0..1."""

    mae: float
    """Mean Absolute Error (pixel-level), 0..1."""

    boundary_recall: float | None = None
    """Recall of shadow boundary pixels, 0..1."""

    def __str__(self) -> str:
        """Format metrics as readable string."""
        lines = [
            "Shadow Detection Metrics",
            "=" * 30,
            f"  IoU:             {self.iou:.4f}",
            f"  Precision:       {self.precision:.4f}",
            f"  Recall:          {self.recall:.4f}",
            f"  F1 Score:        {self.f1:.4f}",
            f"  MAE:             {self.mae:.4f}",
        ]
        if self.boundary_recall is not None:
            lines.append(f"  Boundary Recall: {self.boundary_recall:.4f}")
        return "\n".join(lines)


def compare_shadow_masks(
    pred_mask: np.ndarray,
    gt_mask: np.ndarray,
    compute_boundary_recall: bool = False,
    boundary_width: int = 3,
) -> ShadowEvaluationMetrics:
    """
    Compare predicted and ground-truth shadow masks.

    Args:
        pred_mask: Predicted shadow mask (H×W, 0-255 or binary)
        gt_mask: Ground-truth shadow mask (H×W, 0-255 or binary)
        compute_boundary_recall: Whether to compute boundary-specific recall
        boundary_width: Width of boundary region for boundary_recall

    Returns:
        ShadowEvaluationMetrics with computed metrics

    Notes:
        - Both masks are binarized: values > 127 are considered shadow
        - Suitable for comparing outputs from different detectors
        - Results on standard datasets:
            - ISTD (shadow removal dataset):     IoU ~0.55-0.75 with SOTA
            - SBU (shadow detection):             IoU ~0.45-0.65 with SOTA
            - Synthetic (clean boundaries):       IoU ~0.80-0.95
    """
    # Binarize masks
    pred_binary = (pred_mask > 127).astype(np.float32)
    gt_binary = (gt_mask > 127).astype(np.float32)

    # ========== Standard metrics ==========

    # True positives, false positives, false negatives
    tp = np.sum(pred_binary * gt_binary)
    fp = np.sum(pred_binary * (1 - gt_binary))
    fn = np.sum((1 - pred_binary) * gt_binary)

    # IoU (Intersection over Union)
    intersection = tp
    union = tp + fp + fn
    iou = float(intersection / (union + 1e-8))

    # Precision and Recall
    precision = float(tp / (tp + fp + 1e-8))
    recall = float(tp / (tp + fn + 1e-8))

    # F1 Score
    f1 = float(2 * (precision * recall) / (precision + recall + 1e-8))

    # MAE (Mean Absolute Error, treating masks as float)
    mae = float(np.mean(np.abs(pred_binary - gt_binary)))

    # ========== Boundary Recall (optional) ==========
    boundary_recall = None
    if compute_boundary_recall:
        try:
            import cv2

            # Detect boundaries in GT using Canny or morphological gradient
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (boundary_width, boundary_width))
            gt_boundary = cv2.morphologyEx(
                (gt_binary * 255).astype(np.uint8),
                cv2.MORPH_GRADIENT,
                kernel,
            )
            boundary_pixels = gt_boundary > 0

            if np.any(boundary_pixels):
                # Recall on boundary pixels
                boundary_tp = np.sum(pred_binary[boundary_pixels] * (gt_binary[boundary_pixels]))
                boundary_fn = np.sum(
                    (1 - pred_binary[boundary_pixels]) * (gt_binary[boundary_pixels])
                )
                boundary_recall = float(boundary_tp / (boundary_tp + boundary_fn + 1e-8))
        except ImportError:
            pass

    return ShadowEvaluationMetrics(
        iou=iou,
        precision=precision,
        recall=recall,
        f1=f1,
        mae=mae,
        boundary_recall=boundary_recall,
    )


def compare_soft_masks(
    pred_soft: np.ndarray,
    gt_soft: np.ndarray,
) -> dict[str, float]:
    """
    Compare soft (probabilistic) shadow maps.

    Args:
        pred_soft: Predicted soft map (H×W float32, 0..1)
        gt_soft: Ground-truth soft map (H×W float32, 0..1)

    Returns:
        Dictionary with soft metrics:
            - mae: Mean Absolute Error
            - rmse: Root Mean Squared Error
            - ssim: Structural Similarity Index (requires scikit-image)
            - correlation: Pearson correlation coefficient
    """
    # Ensure float32
    pred = np.clip(pred_soft, 0, 1).astype(np.float32)
    gt = np.clip(gt_soft, 0, 1).astype(np.float32)

    # MAE and RMSE
    mae = float(np.mean(np.abs(pred - gt)))
    rmse = float(np.sqrt(np.mean((pred - gt) ** 2)))

    # Correlation
    pred_flat = pred.flatten()
    gt_flat = gt.flatten()
    correlation = float(np.corrcoef(pred_flat, gt_flat)[0, 1])

    # SSIM (optional)
    ssim = None
    try:
        from skimage.metrics import structural_similarity

        ssim = float(structural_similarity(pred, gt, data_range=1.0))
    except ImportError:
        pass

    metrics = {
        "mae": mae,
        "rmse": rmse,
        "correlation": correlation,
    }
    if ssim is not None:
        metrics["ssim"] = ssim

    return metrics


def evaluate_multi_method_comparison(
    gt_mask: np.ndarray,
    pred_masks: dict[str, np.ndarray],
    show_comparison: bool = False,
) -> dict[str, ShadowEvaluationMetrics]:
    """
    Compare multiple shadow detection methods against ground truth.

    Args:
        gt_mask: Ground-truth mask (H×W)
        pred_masks: Dictionary mapping method names to predicted masks
        show_comparison: If True, print comparison table

    Returns:
        Dictionary mapping method names to ShadowEvaluationMetrics

    Example:
        >>> gt = cv2.imread("shadow_gt.png", 0)
        >>> pred_cv = detect_shadows_classical(image)["shadow_mask"]
        >>> pred_ai = extract_shadows_ai(image)["mask"]
        >>> results = evaluate_multi_method_comparison(
        ...     gt, {"CV": pred_cv, "AI": pred_ai}
        ... )
        >>> for method, metrics in results.items():
        ...     print(f"{method}: IoU={metrics.iou:.3f}, F1={metrics.f1:.3f}")
    """
    results = {}

    for method_name, pred_mask in pred_masks.items():
        metrics = compare_shadow_masks(pred_mask, gt_mask)
        results[method_name] = metrics

    if show_comparison:
        print("=" * 60)
        print("Shadow Detection Method Comparison")
        print("=" * 60)
        print(f"{'Method':<15} {'IoU':<10} {'Precision':<12} {'Recall':<10} {'F1':<10}")
        print("-" * 60)

        for method_name, metrics in results.items():
            print(
                f"{method_name:<15} {metrics.iou:<10.4f} {metrics.precision:<12.4f} "
                f"{metrics.recall:<10.4f} {metrics.f1:<10.4f}"
            )

        print("=" * 60)

    return results
