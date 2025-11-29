"""
Lightweight CV-first spacing extractor (OpenCV gap analysis).

Adds prominence metadata and base unit/scale info for UI display.
"""

from __future__ import annotations

import base64
from typing import Any

try:
    import cv2
except ImportError:  # pragma: no cover - fallback path when OpenCV is absent
    cv2 = None  # type: ignore[assignment]
import numpy as np

from copy_that.application import spacing_utils as su
from copy_that.application.cv.debug_spacing import generate_spacing_overlay
from copy_that.application.cv.grid_cv_extractor import infer_grid_from_bboxes
from copy_that.application.spacing_models import (
    SpacingExtractionResult,
    SpacingScale,
    SpacingToken,
    SpacingType,
)
from cv_pipeline.preprocess import preprocess_image
from cv_pipeline.primitives import components_to_bboxes, gaps_from_bboxes

SNAP_TOLERANCE_PX = 2.0


class CVSpacingExtractor:
    """Fast spacing inference without remote AI."""

    def __init__(self, max_tokens: int = 12, expected_base_px: int | None = None):
        self.max_tokens = max_tokens
        self.expected_base_px = expected_base_px

    def extract_from_bytes(self, data: bytes) -> SpacingExtractionResult:
        if cv2 is None:
            return self._fallback()
        try:
            views = preprocess_image(data)
            gray = views["cv_gray"]
        except Exception:
            return self._fallback()

        bboxes = components_to_bboxes(gray)
        if len(bboxes) < 2:
            return self._fallback()

        x_gaps, y_gaps = gaps_from_bboxes(bboxes)
        all_gaps = [float(v) for v in x_gaps + y_gaps]
        guides = self._detect_guides(gray)
        all_gaps = self._snap_gaps_to_guides(gray, all_gaps)
        if not all_gaps:
            return self._fallback()

        base_unit, base_confidence, normalized_values = su.infer_base_spacing_robust(all_gaps)
        if not normalized_values:
            normalized_values = su.cluster_spacing_values(all_gaps, tolerance=0.15)
        if not normalized_values:
            return self._fallback()
        base_alignment = su.compare_base_units(self.expected_base_px, base_unit, tolerance=1)
        counts: dict[int, int] = dict.fromkeys(normalized_values, 0)
        for gap in all_gaps:
            nearest = min(normalized_values, key=lambda candidate: abs(candidate - gap))
            counts[nearest] = counts.get(nearest, 0) + 1
        values = normalized_values[: self.max_tokens]
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

        baseline_spacing = su.detect_baseline_spacing_from_bboxes(bboxes)
        if baseline_spacing:
            baseline_value, baseline_conf = baseline_spacing
            if baseline_value > 0:
                if baseline_value not in values:
                    values.append(baseline_value)
                    values.sort()
                tokens.append(
                    SpacingToken(
                        value_px=int(baseline_value),
                        name="spacing-baseline",
                        semantic_role="baseline rhythm",
                        spacing_type=SpacingType.STACK,
                        category="cv",
                        confidence=min(0.95, 0.5 + 0.4 * baseline_conf),
                        usage=["typography"],
                        scale_position=len(values) - 1,
                        base_unit=base_unit,
                        scale_system=self._scale_from_base(base_unit),
                        grid_aligned=base_unit > 0 and baseline_value % base_unit == 0,
                        prominence_percentage=None,
                        extraction_metadata={
                            "source": "cv",
                            "baseline_confidence": baseline_conf,
                        },
                    )
                )
        else:
            baseline_spacing = None

        component_metrics = self._infer_component_spacing_metrics(bboxes, gray.shape, gray)
        grid_detection = infer_grid_from_bboxes(bboxes, canvas_width=gray.shape[1])
        debug_overlay = generate_spacing_overlay(
            gray,
            bboxes,
            base_unit=base_unit,
            guides=guides,
            baseline_spacing=int(baseline_spacing[0]) if baseline_spacing else None,
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
            cv_gap_diagnostics=su.cross_check_gaps(all_gaps, base_unit, tolerance_px=1.0),
            base_alignment=base_alignment,
            cv_gaps_sample=all_gaps[:20],
            baseline_spacing={"value_px": baseline_spacing[0], "confidence": baseline_spacing[1]}
            if baseline_spacing
            else None,
            component_spacing_metrics=component_metrics or None,
            grid_detection=grid_detection,
            debug_overlay=debug_overlay,
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
            cv_gap_diagnostics=None,
            base_alignment=su.compare_base_units(None, 4, tolerance=1),
            cv_gaps_sample=None,
            baseline_spacing=None,
            component_spacing_metrics=None,
            grid_detection=None,
        )

    @staticmethod
    def _is_child(inner: tuple[int, int, int, int], outer: tuple[int, int, int, int]) -> bool:
        tolerance = 2
        ix, iy, iw, ih = inner
        ox, oy, ow, oh = outer
        return (
            ix >= ox + tolerance
            and iy >= oy + tolerance
            and ix + iw <= ox + ow - tolerance
            and iy + ih <= oy + oh - tolerance
        )

    @staticmethod
    def _neighbor_gap(
        target: tuple[int, int, int, int],
        bboxes: list[tuple[int, int, int, int]],
    ) -> float | None:
        tx, ty, tw, th = target
        tx2 = tx + tw
        ty2 = ty + th
        gaps: list[float] = []
        for box in bboxes:
            if box is target:
                continue
            x, y, w, h = box
            x2 = x + w
            y2 = y + h
            if x >= tx2:
                gaps.append(x - tx2)
            elif tx >= x2:
                gaps.append(tx - x2)
            if y >= ty2:
                gaps.append(y - ty2)
            elif ty >= y2:
                gaps.append(ty - y2)
        if not gaps:
            return None
        return min(gaps)

    def _snap_gaps_to_guides(self, gray: Any, gaps: list[float]) -> list[float]:
        """Use distance transform bands and Hough line guides to snap noisy gaps."""
        if cv2 is None or not gaps:
            return gaps

        candidates: list[float] = []
        try:
            # Distance transform on inverted binary image; ridge height ~ half gap.
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            inverted = 255 - binary
            dist = cv2.distanceTransform(inverted, cv2.DIST_L2, 3)
            if dist.size > 0:
                max_val = float(np.max(dist))
                if max_val > 1.0:
                    hist, bin_edges = np.histogram(dist, bins=32, range=(0.0, max_val))
                    peak_idx = int(hist.argmax())
                    peak_val = (bin_edges[peak_idx] + bin_edges[peak_idx + 1]) / 2.0
                    candidates.append(float(peak_val * 2.0))
        except Exception:
            pass

        try:
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(
                edges, 1, np.pi / 180, threshold=40, minLineLength=40, maxLineGap=8
            )
            if lines is not None:
                vertical_centers: list[int] = []
                horizontal_centers: list[int] = []
                for x1, y1, x2, y2 in lines[:, 0]:
                    dx = abs(x2 - x1)
                    dy = abs(y2 - y1)
                    if dx < dy * 0.3:  # vertical-ish
                        vertical_centers.append(int(round((x1 + x2) / 2)))
                    elif dy < dx * 0.3:  # horizontal-ish
                        horizontal_centers.append(int(round((y1 + y2) / 2)))
                vertical_centers.sort()
                horizontal_centers.sort()

                def _add_diffs(vals: list[int]) -> None:
                    for i in range(len(vals) - 1):
                        diff = vals[i + 1] - vals[i]
                        if diff > 0:
                            candidates.append(float(diff))

                if len(vertical_centers) >= 2:
                    _add_diffs(vertical_centers)
                if len(horizontal_centers) >= 2:
                    _add_diffs(horizontal_centers)
        except Exception:
            pass

        if not candidates:
            return gaps

        snapped: list[float] = []
        for g in gaps:
            nearest = min(candidates, key=lambda c: abs(c - g))
            if abs(nearest - g) <= SNAP_TOLERANCE_PX:
                snapped.append(float(round(nearest)))
            else:
                snapped.append(g)
        return snapped

    def _detect_guides(self, gray: Any) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        if cv2 is None:
            return []
        try:
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(
                edges, 1, np.pi / 180, threshold=40, minLineLength=40, maxLineGap=8
            )
            guides: list[tuple[tuple[int, int], tuple[int, int]]] = []
            if lines is not None:
                for x1, y1, x2, y2 in lines[:, 0]:
                    guides.append(((int(x1), int(y1)), (int(x2), int(y2))))
            return guides
        except Exception:
            return []

    def _infer_component_spacing_metrics(
        self,
        bboxes: list[tuple[int, int, int, int]],
        canvas_shape: tuple[int, int],
        gray: Any | None,
    ) -> list[dict[str, Any]]:
        height, width = canvas_shape
        metrics: list[dict[str, Any]] = []
        for idx, outer in enumerate(bboxes):
            ox, oy, ow, oh = outer
            outer_area = max(ow * oh, 1)
            children = [
                child for child in bboxes if child is not outer and self._is_child(child, outer)
            ]
            padding: dict[str, int] | None = None
            padding_conf = 0.0
            if children:
                cx1 = min(child[0] for child in children)
                cy1 = min(child[1] for child in children)
                cx2 = max(child[0] + child[2] for child in children)
                cy2 = max(child[1] + child[3] for child in children)
                padding = {
                    "top": max(0, cy1 - oy),
                    "bottom": max(0, (oy + oh) - cy2),
                    "left": max(0, cx1 - ox),
                    "right": max(0, (ox + ow) - cx2),
                }
                child_area = sum(child[2] * child[3] for child in children)
                padding_conf = min(1.0, child_area / outer_area)
            # If no explicit children, attempt simple text/inner ROI detection
            if padding is None and gray is not None:
                roi = gray[oy : oy + oh, ox : ox + ow]
                try:
                    _, th = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)  # type: ignore[arg-type]
                    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # type: ignore[assignment]
                    contours = [c for c in contours if cv2.contourArea(c) > 8]  # type: ignore[operator]
                    if contours:
                        largest = max(contours, key=cv2.contourArea)  # type: ignore[arg-type]
                        x, y, w, h = cv2.boundingRect(largest)
                        padding = {
                            "top": max(0, y),
                            "bottom": max(0, oh - (y + h)),
                            "left": max(0, x),
                            "right": max(0, ow - (x + h)),
                        }
                        padding_conf = min(1.0, (w * h) / outer_area)
                except Exception:
                    padding = None

            if padding is None:
                continue
            margins = {
                "top": max(0, oy),
                "bottom": max(0, height - (oy + oh)),
                "left": max(0, ox),
                "right": max(0, width - (ox + ow)),
            }
            metrics.append(
                {
                    "index": idx,
                    "box": [ox, oy, ow, oh],
                    "padding": padding,
                    "padding_confidence": round(padding_conf, 4),
                    "margin": margins,
                    "neighbor_gap": self._neighbor_gap(outer, bboxes),
                }
            )
        return metrics
