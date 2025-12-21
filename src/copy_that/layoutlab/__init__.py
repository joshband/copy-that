"""Lightweight layout lab utilities (detectors, depth estimators)."""

from .layout_detector import detect_layout_primitives
from .depth_estimator import (
    DepthMap,
    classify_spacing_depth,
    depth_scores_for_boxes,
    estimate_depth_map,
)
from .elevation_tokens import derive_elevation_tokens, summarize_lighting
from .shape_inference import estimate_border_width, estimate_corner_radius

__all__ = [
    "DepthMap",
    "classify_spacing_depth",
    "depth_scores_for_boxes",
    "detect_layout_primitives",
    "estimate_depth_map",
    "derive_elevation_tokens",
    "summarize_lighting",
    "estimate_corner_radius",
    "estimate_border_width",
]
