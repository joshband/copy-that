"""Shared CV helpers used by extractors (FastSAM, UIED, debug overlays, layout).

Shared FastSAM/UIED/debug/grid helpers for extractors.
Application modules re-export these for backward compatibility.
"""

from __future__ import annotations

__all__ = [
    "debug_color",
    "debug_spacing",
    "fastsam_segmenter",
    "grid_cv_extractor",
    "layout_text_detector",
    "uied_integration",
]
