"""
Lightweight CV-first spacing extractor (OpenCV gap analysis).

Adds prominence metadata and base unit/scale info for UI display.
"""

from __future__ import annotations

import base64
import logging
import os
from typing import Any, cast

from PIL import Image

try:
    import cv2
except ImportError:  # pragma: no cover - fallback path when OpenCV is absent
    cv2 = None  # type: ignore[assignment]
import numpy as np

from copy_that.application import color_utils
from copy_that.application import spacing_utils as su
from copy_that.application.cv.debug_spacing import generate_spacing_overlay
from copy_that.application.cv.fastsam_segmenter import FastSAMRegion, FastSAMSegmenter
from copy_that.application.cv.grid_cv_extractor import infer_grid_from_bboxes
from copy_that.application.cv.layout_text_detector import (
    ImageMode,
    TextToken,
    attach_text_to_components,
    detect_image_mode,
    run_layoutparser_text,
)
from copy_that.application.cv.uied_integration import run_uied
from copy_that.application.spacing_models import (
    SpacingExtractionResult,
    SpacingScale,
    SpacingToken,
    SpacingType,
)
from cv_pipeline.preprocess import preprocess_image
from cv_pipeline.primitives import components_to_bboxes, gaps_from_bboxes

SNAP_TOLERANCE_PX = 2.0
logger = logging.getLogger(__name__)


class CVSpacingExtractor:
    """Fast spacing inference without remote AI."""

    def __init__(
        self,
        max_tokens: int = 12,
        expected_base_px: int | None = None,
        fastsam_model_path: str | None = None,
        fastsam_device: str = "cpu",
        fastsam_enabled: bool | None = None,
        image_mode: str | None = None,
    ):
        self.max_tokens = max_tokens
        self.expected_base_px = expected_base_px
        enabled_env = os.getenv("FASTSAM_ENABLED")
        self._fastsam_enabled = (
            fastsam_enabled
            if fastsam_enabled is not None
            else (enabled_env is None or enabled_env != "0")
        )
        self._fastsam_model_path = (
            fastsam_model_path
            or os.getenv("FASTSAM_MODEL_PATH")
            or ("FastSAM-s.pt" if self._fastsam_enabled else None)
        )
        self._fastsam_device = os.getenv("FASTSAM_DEVICE", fastsam_device)
        self._fastsam: FastSAMSegmenter | None = None
        self.image_mode = image_mode
        lp_env = os.getenv("ENABLE_LAYOUTPARSER_TEXT")
        self._lp_enabled = lp_env not in {"0", "false", "False"} if lp_env is not None else True
        uied_env = os.getenv("ENABLE_UIED", "1")
        self._uied_enabled = uied_env not in {"0", "false", "False"}

    @staticmethod
    def _iou(box_a: tuple[int, int, int, int], box_b: tuple[int, int, int, int]) -> float:
        ax, ay, aw, ah = box_a
        bx, by, bw, bh = box_b
        ax2, ay2, bx2, by2 = ax + aw, ay + ah, bx + bw, by + bh
        inter_x1, inter_y1 = max(ax, bx), max(ay, by)
        inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
        inter_w, inter_h = max(0, inter_x2 - inter_x1), max(0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h
        if inter_area <= 0:
            return 0.0
        area_a = aw * ah
        area_b = bw * bh
        return inter_area / float(area_a + area_b - inter_area + 1e-6)

    def _classify_element(
        self,
        metric: dict[str, Any],
        uied_tokens: list[dict[str, Any]] | None,
    ) -> str:
        box = metric.get("box") or metric.get("bbox")
        if not box or len(box) != 4:
            return "unknown"
        x, y, w, h = [int(v) for v in box]
        area = max(w * h, 1)
        aspect = w / max(h, 1)
        text = metric.get("text") or metric.get("label")

        if uied_tokens:
            best = None
            best_iou = 0.0
            for tok in uied_tokens:
                tb = tok.get("bbox")
                if not tb or len(tb) != 4:
                    continue
                ov = self._iou(tuple(box), tuple(tb))
                if ov > best_iou:
                    best_iou = ov
                    best = tok
            if best and best_iou >= 0.3:
                return str(best.get("type") or best.get("uied_label") or "component").lower()

        if text:
            if w <= 180 and h <= 80:
                return "button"
            return "container"
        if w < 40 and h < 40:
            return "icon"
        if area > 6000 and 0.5 <= aspect <= 1.8:
            return "image"
        if w > 200 and h > 120:
            return "container"
        return "graphic"

    def _merge_fastsam_into_components(
        self,
        fastsam_tokens: list[dict[str, Any]] | None,
        component_metrics: list[dict[str, Any]] | None,
        iou_threshold: float = 0.5,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if not fastsam_tokens or not component_metrics:
            return component_metrics or [], fastsam_tokens or []
        remaining: list[dict[str, Any]] = []
        merged: list[dict[str, Any]] = []
        for token in fastsam_tokens:
            tb = token.get("bbox")
            if not tb or len(tb) != 4:
                remaining.append(token)
                continue
            best = None
            best_iou = 0.0
            for metric in component_metrics:
                box = metric.get("box") or metric.get("bbox")
                if not box or len(box) != 4:
                    continue
                ov = self._iou(tuple(box), tuple(tb))
                if ov > best_iou:
                    best_iou = ov
                    best = metric
            if best and best_iou >= iou_threshold:
                best["fastsam_bbox"] = tb
                best["fastsam_polygon"] = token.get("polygon")
                best["fastsam_area"] = token.get("area")
                merged.append(token)
            else:
                remaining.append(token)
        return component_metrics, remaining

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
        pil_img = (
            views.get("pil_image") if isinstance(views.get("pil_image"), Image.Image) else None
        )
        fastsam_regions: list[FastSAMRegion] = []
        fastsam_tokens: list[dict[str, Any]] = []
        if self._fastsam_enabled and self._fastsam_model_path:
            try:
                if self._fastsam is None:
                    self._fastsam = FastSAMSegmenter(
                        self._fastsam_model_path, device=self._fastsam_device
                    )
                fastsam_input = pil_img or views.get("cv_bgr")
                if fastsam_input is not None:
                    fastsam_regions = self._fastsam.segment(fastsam_input)
                if pil_img is not None and fastsam_regions:
                    w, h = pil_img.size
                    min_area = max(int(w * h * 0.001), 150)
                    fastsam_regions = [r for r in fastsam_regions if r.area >= min_area]
                for idx, region in enumerate(fastsam_regions):
                    fastsam_tokens.append(
                        {
                            "id": f"fastsam-{idx + 1}",
                            "type": "segment",
                            "bbox": region.bbox,
                            "area": region.area,
                            "polygon": region.polygon,
                            "has_mask": region.mask is not None,
                            "source": "fastsam",
                        }
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("FastSAM segmentation skipped: %s", exc)
                fastsam_regions = []
                fastsam_tokens = []
        if component_metrics and fastsam_tokens:
            component_metrics, fastsam_tokens = self._merge_fastsam_into_components(
                fastsam_tokens, component_metrics, iou_threshold=0.5
            )
        if component_metrics and pil_img is not None:
            width, height = pil_img.size
            enriched: list[dict[str, Any]] = []
            for metric in component_metrics:
                box = metric.get("box") if isinstance(metric, dict) else None
                if not box or len(box) != 4:
                    enriched.append(metric)
                    continue
                x, y, w, h = [int(v) for v in box]
                if w <= 0 or h <= 0:
                    enriched.append(metric)
                    continue
                x1 = max(x, 0)
                y1 = max(y, 0)
                x2 = min(x1 + w, width)
                y2 = min(y1 + h, height)
                if x2 <= x1 or y2 <= y1:
                    enriched.append(metric)
                    continue
                region: Image.Image = pil_img.crop((x1, y1, x2, y2))
                palette = color_utils.dominant_colors_from_region(region, max_colors=2)
                colors = None
                if palette:
                    colors = {
                        "primary": palette[0]["hex"],
                        "secondary": palette[1]["hex"] if len(palette) > 1 else None,
                        "palette": [p["hex"] for p in palette],
                    }
                enriched.append({**metric, "colors": colors})
            component_metrics = enriched
        alignment = su.detect_alignment_lines(bboxes, tolerance=3, min_support=2)
        gap_clusters = {
            "x": su.cluster_gaps([gap for gap in x_gaps if gap > 0]),
            "y": su.cluster_gaps([gap for gap in y_gaps if gap > 0]),
        }
        text_tokens: list[TextToken] = []
        if pil_img is not None:
            try:
                mode = (
                    cast(ImageMode, self.image_mode)
                    if self.image_mode
                    else detect_image_mode(pil_img)
                )
                text_tokens = run_layoutparser_text(pil_img, mode, enabled=self._lp_enabled)
                if text_tokens and component_metrics:
                    component_metrics, residual_text = attach_text_to_components(
                        component_metrics, text_tokens
                    )
                    text_tokens = residual_text
            except Exception as exc:  # noqa: BLE001
                logger.warning("LayoutParser text detection skipped: %s", exc)

        uied_tokens: list[dict[str, Any]] = []
        if pil_img is not None and self._uied_enabled:
            try:
                uied_tokens = run_uied(pil_img)
            except Exception as exc:  # noqa: BLE001
                logger.warning("UIED integration skipped: %s", exc)

        graph_inputs: list[dict[str, Any]] = list(component_metrics or [])
        if fastsam_tokens:
            graph_inputs.extend(fastsam_tokens)
        if text_tokens:
            graph_inputs.extend(
                [
                    {
                        "id": t.id,
                        "box": [*t.bbox],
                        "type": "text",
                        "text": t.text,
                        "score": t.score,
                        "source": t.source,
                    }
                    for t in text_tokens
                ]
            )
        if uied_tokens:
            graph_inputs.extend(
                [
                    {
                        "id": t.get("id"),
                        "box": list(t.get("bbox", [])),
                        "type": t.get("type"),
                        "text": t.get("text"),
                        "source": t.get("source"),
                        "uied_label": t.get("uied_label"),
                        "element_type": t.get("element_type"),
                    }
                    for t in uied_tokens
                    if t.get("bbox")
                ]
            )
        if component_metrics:
            enriched = []
            for metric in component_metrics:
                element_type = self._classify_element(metric, uied_tokens)
                enriched.append({**metric, "element_type": element_type})
            component_metrics = enriched
        if uied_tokens:
            for tok in uied_tokens:
                tok.setdefault("element_type", tok.get("type"))

        token_graph = su.build_token_graph(graph_inputs, tolerance=2, min_coverage=0.75)
        fastsam_payload = None
        if fastsam_regions:
            fastsam_payload = [
                {
                    "bbox": region.bbox,
                    "area": region.area,
                    "has_mask": region.mask is not None,
                    "polygon": region.polygon,
                }
                for region in fastsam_regions
            ]
        validation = su.validate_extraction(
            component_metrics or fastsam_tokens or [],
            (gray.shape[1], gray.shape[0]),
        )
        debug_overlay = None
        if isinstance(gray, np.ndarray):
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
            warnings=validation.get("warnings"),
            alignment=alignment,
            gap_clusters=gap_clusters,
            token_graph=token_graph or None,
            fastsam_regions=fastsam_payload,
            fastsam_tokens=fastsam_tokens,
            text_tokens=(
                [
                    {
                        "id": t.id,
                        "type": t.type,
                        "bbox": t.bbox,
                        "text": t.text,
                        "score": t.score,
                        "source": t.source,
                    }
                    for t in text_tokens
                ]
                if text_tokens
                else None
            ),
            uied_tokens=uied_tokens or None,
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
        if cv2 is None or not isinstance(gray, np.ndarray):
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
            if padding is None and isinstance(gray, np.ndarray):
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
