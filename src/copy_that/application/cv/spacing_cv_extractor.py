"""
Lightweight CV-first spacing extractor (OpenCV gap analysis).

Adds prominence metadata and base unit/scale info for UI display.
"""

from __future__ import annotations

import base64
from collections import Counter
from collections.abc import Iterable

try:
    import cv2
except ImportError:  # pragma: no cover - fallback path when OpenCV is absent
    cv2 = None  # type: ignore[assignment]

from copy_that.application.spacing_models import (
    SpacingExtractionResult,
    SpacingScale,
    SpacingToken,
)
from cv_pipeline.preprocess import preprocess_image


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

        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return self._fallback()

        raw_bboxes = [cv2.boundingRect(c) for c in contours]
        bboxes: list[tuple[int, int, int, int]] = [
            (int(x), int(y), int(w), int(h)) for x, y, w, h in raw_bboxes
        ]
        if len(bboxes) < 2:
            return self._fallback()

        x_gaps, y_gaps = self._measure_gaps(bboxes)
        all_gaps = x_gaps + y_gaps
        if not all_gaps:
            return self._fallback()

        quantized = [self._quantize(g) for g in all_gaps if g > 0]
        counts = Counter(quantized)
        common = counts.most_common(self.max_tokens)
        values = sorted(set([v for v, _ in common]))[: self.max_tokens]
        if not values:
            return self._fallback()

        base_unit = self._detect_base_unit(values)
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
    def _measure_gaps(bboxes: Iterable[tuple[int, int, int, int]]) -> tuple[list[int], list[int]]:
        x_gaps: list[int] = []
        y_gaps: list[int] = []
        sorted_x = sorted(bboxes, key=lambda b: b[0])
        sorted_y = sorted(bboxes, key=lambda b: b[1])
        for i in range(len(sorted_x) - 1):
            _, _, w1, _ = sorted_x[i]
            x1 = sorted_x[i][0] + w1
            x2 = sorted_x[i + 1][0]
            gap = x2 - x1
            if 2 <= gap <= 200:
                x_gaps.append(gap)
        for i in range(len(sorted_y) - 1):
            _, _, _, h1 = sorted_y[i]
            y1 = sorted_y[i][1] + h1
            y2 = sorted_y[i + 1][1]
            gap = y2 - y1
            if 2 <= gap <= 200:
                y_gaps.append(gap)
        return x_gaps, y_gaps

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
        return SpacingExtractionResult(
            tokens=tokens,
            scale_system=SpacingScale.FOUR_POINT,
            base_unit=4,
            grid_compliance=1.0,
            extraction_confidence=0.5,
            min_spacing=min(defaults),
            max_spacing=max(defaults),
            unique_values=defaults,
        )
