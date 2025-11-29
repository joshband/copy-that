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
from copy_that.application.cv.grid_cv_extractor import infer_grid_from_bboxes
from copy_that.application.spacing_models import (
    SpacingExtractionResult,
    SpacingScale,
    SpacingToken,
    SpacingType,
)
from cv_pipeline.preprocess import preprocess_image
from cv_pipeline.primitives import components_to_bboxes, gaps_from_bboxes


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

        component_metrics = self._infer_component_spacing_metrics(bboxes, gray.shape)
        grid_detection = infer_grid_from_bboxes(bboxes, canvas_width=gray.shape[1])

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

    def _infer_component_spacing_metrics(
        self, bboxes: list[tuple[int, int, int, int]], canvas_shape: tuple[int, int]
    ) -> list[dict]:
        height, width = canvas_shape
        metrics: list[dict] = []
        for idx, outer in enumerate(bboxes):
            ox, oy, ow, oh = outer
            outer_area = max(ow * oh, 1)
            children = [
                child for child in bboxes if child is not outer and self._is_child(child, outer)
            ]
            if not children:
                continue
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
