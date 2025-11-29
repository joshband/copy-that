"""
Lightweight CV-first spacing extractor (OpenCV gap analysis).

Adds prominence metadata and base unit/scale info for UI display.
"""

from __future__ import annotations

import base64

try:
    import cv2
except ImportError:  # pragma: no cover - fallback path when OpenCV is absent
    cv2 = None  # type: ignore[assignment]

from copy_that.application import spacing_utils as su
from copy_that.application.spacing_models import (
    SpacingExtractionResult,
    SpacingScale,
    SpacingToken,
)
from cv_pipeline.preprocess import preprocess_image
from cv_pipeline.primitives import bounding_boxes_from_contours, measure_spacing_gaps


class CVSpacingExtractor:
    """Fast spacing inference without remote AI."""

    def __init__(self, max_tokens: int = 12):
        self.max_tokens = max_tokens

    def extract_from_bytes(self, data: bytes) -> SpacingExtractionResult:
        if cv2 is None:
            return self._fallback()
        try:
            views = preprocess_image(data)
            gray = views["cv_gray"]
        except Exception:
            return self._fallback()

        bboxes = bounding_boxes_from_contours(gray)
        if len(bboxes) < 2:
            return self._fallback()

        x_gaps, y_gaps = measure_spacing_gaps(bboxes)
        all_gaps = [float(v) for v in x_gaps + y_gaps]
        if not all_gaps:
            return self._fallback()

        clustered = su.cluster_spacing_values(all_gaps, tolerance=0.15)
        if not clustered:
            return self._fallback()
        base_unit, base_confidence = su.infer_base_spacing(clustered)
        counts = {v: all_gaps.count(v) for v in clustered}
        values = clustered[: self.max_tokens]
        tokens: list[SpacingToken] = []
        for i, (label, v) in enumerate(zip(self._labels(), values, strict=False)):
            prominence = counts.get(v, 1) / max(len(all_gaps), 1)
            tokens.append(
                SpacingToken(
                    value_px=int(v),
                    name=f"spacing-{label}",
                    semantic_role="layout",
                    spacing_type=None,
                    category="cv",
                    confidence=0.55 + (0.1 * min(prominence, 0.3)),
                    usage=["layout"],
                    scale_position=i,
                    base_unit=base_unit,
                    scale_system=self._scale_from_base(base_unit),
                    grid_aligned=base_unit > 0 and v % base_unit == 0,
                    prominence_percentage=round(prominence * 100, 2),
                    extraction_metadata={"source": "cv"},
                )
            )

        return SpacingExtractionResult(
            tokens=tokens,
            scale_system=self._scale_from_base(base_unit),
            base_unit=base_unit,
            base_unit_confidence=base_confidence,
            grid_compliance=1.0 if base_unit else 0.5,
            extraction_confidence=0.55,
            min_spacing=min(values),
            max_spacing=max(values),
            unique_values=values,
        )

    def extract_from_base64(self, image_base64: str) -> SpacingExtractionResult:
        data = base64.b64decode(image_base64.split(",")[1] if "," in image_base64 else image_base64)
        return self.extract_from_bytes(data)

    @staticmethod
    def _quantize(val: int) -> int:
        return int(round(val / 4.0) * 4)

    @staticmethod
    def _detect_base_unit(values: list[int]) -> int:
        if all(v % 8 == 0 for v in values):
            return 8
        if all(v % 4 == 0 for v in values):
            return 4
        return 4

    @staticmethod
    def _scale_from_base(base: int) -> SpacingScale:
        return SpacingScale.EIGHT_POINT if base >= 8 else SpacingScale.FOUR_POINT

    @staticmethod
    def _labels() -> list[str]:
        return ["xs", "sm", "md", "lg", "xl", "xxl", "xxxl", "mega"]

    @staticmethod
    def _fallback() -> SpacingExtractionResult:
        defaults = [4, 8, 16, 24, 32, 48]
        tokens = [
            SpacingToken(
                value_px=v,
                name=f"spacing-{n}",
                semantic_role="layout",
                spacing_type=None,
                category="cv",
                confidence=0.5,
                usage=["layout"],
                scale_position=i,
                base_unit=4,
                scale_system=SpacingScale.FOUR_POINT,
                grid_aligned=True,
                prominence_percentage=None,
                extraction_metadata={"source": "cv"},
            )
            for i, (n, v) in enumerate(
                zip(["xs", "sm", "md", "lg", "xl", "xxl"], defaults, strict=False)
            )
        ]
        base_unit, base_confidence = su.infer_base_spacing(defaults)
        return SpacingExtractionResult(
            tokens=tokens,
            scale_system=SpacingScale.FOUR_POINT,
            base_unit=4,
            base_unit_confidence=base_confidence,
            grid_compliance=1.0,
            extraction_confidence=0.5,
            min_spacing=min(defaults),
            max_spacing=max(defaults),
            unique_values=defaults,
        )
