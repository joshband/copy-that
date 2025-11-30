"""
Multi-modal extraction orchestrator.

Combines CV tokenization, FastSAM segmentation, LayoutParser text, UIED, graph building,
and heuristic classification via CVSpacingExtractor toggles.
"""

from __future__ import annotations

import io
import logging
from typing import Literal

from PIL import Image

from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor
from copy_that.application.spacing_models import SpacingExtractionResult

logger = logging.getLogger(__name__)


def extract_ui(
    image: Image.Image | bytes,
    *,
    use_fastsam: bool = True,
    use_layout: bool = True,
    use_uied: bool = True,
    expected_base_px: int | None = None,
    image_mode: Literal["ui_screenshot", "photo", "ai_panel"] | None = None,
) -> SpacingExtractionResult:
    """
    Run the multi-modal pipeline with configurable toggles.

    Steps:
    1. CV spacing/tokenization.
    2. FastSAM segmentation (optional).
    3. LayoutParser text/OCR (optional).
    4. UIED ensemble (optional).
    5. Token graph + heuristic classification.

    Args:
        image: PIL image or raw bytes.
        use_fastsam: Enable FastSAM segmentation.
        use_layout: Enable LayoutParser text detection.
        use_uied: Enable UIED ensemble (requires UIED_RUNNER).
        expected_base_px: Optional expected base spacing.
        image_mode: Optional override for image mode heuristics.
    """
    extractor = CVSpacingExtractor(
        expected_base_px=expected_base_px,
        fastsam_enabled=use_fastsam,
        image_mode=image_mode,
    )
    # Override toggles
    extractor._lp_enabled = extractor._lp_enabled and use_layout
    extractor._uied_enabled = extractor._uied_enabled and use_uied

    if isinstance(image, Image.Image):
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return extractor.extract_from_bytes(buf.getvalue())
    if isinstance(image, (bytes, bytearray)):
        return extractor.extract_from_bytes(bytes(image))
    raise TypeError("image must be PIL.Image or bytes")
