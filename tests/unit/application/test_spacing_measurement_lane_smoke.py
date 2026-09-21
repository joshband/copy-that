import io

import pytest

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]

import numpy as np

from copy_that.extractors.spacing.cv_extractor import CVSpacingExtractor


def _encode_png(gray: np.ndarray) -> bytes:
    if cv2 is not None:
        ok, buf = cv2.imencode(".png", gray)
        assert ok
        return bytes(buf)
    from PIL import Image

    out = io.BytesIO()
    Image.fromarray(gray).save(out, format="PNG")
    return out.getvalue()


def _make_layout(layout_id: int) -> np.ndarray:
    canvas = np.full((240, 360), 255, dtype=np.uint8)

    def rect(x: int, y: int, w: int, h: int, *, thickness: int = -1) -> None:
        if cv2 is None:
            raise RuntimeError("cv2 required for synthetic layouts")
        cv2.rectangle(canvas, (x, y), (x + w, y + h), 0, thickness)

    # 12 deterministic "test images" with varied adjacency/padding layouts.
    if layout_id == 0:
        # Row: two equal gaps (16px)
        rect(20, 40, 40, 40)
        rect(76, 40, 40, 40)
        rect(132, 40, 40, 40)
    elif layout_id == 1:
        # Column: two equal gaps (20px)
        rect(40, 20, 40, 40)
        rect(40, 80, 40, 40)
        rect(40, 140, 40, 40)
    elif layout_id == 2:
        # 2x2 grid: x gaps 18px, y gaps 22px
        rect(20, 20, 30, 30)
        rect(68, 20, 30, 30)
        rect(20, 72, 30, 30)
        rect(68, 72, 30, 30)
    elif layout_id == 3:
        # Staggered row with strong vertical overlap
        rect(20, 30, 60, 30)
        rect(100, 35, 60, 24)
        rect(180, 28, 60, 34)
    elif layout_id == 4:
        # Two columns, mixed widths/heights; tests overlap gating
        rect(30, 30, 90, 26)
        rect(140, 34, 70, 22)
        rect(30, 80, 60, 24)
        rect(110, 86, 100, 20)
    elif layout_id == 5:
        # Overlap + valid adjacency elsewhere
        rect(20, 20, 70, 40)
        rect(60, 30, 70, 40)  # overlaps (no gap)
        rect(160, 20, 50, 40)  # creates a gap from the rightmost overlapped region
    elif layout_id == 6:
        # Thin "text" bars in a vertical stack
        rect(30, 20, 160, 10)
        rect(30, 44, 120, 10)
        rect(30, 68, 180, 10)
        rect(30, 92, 140, 10)
    elif layout_id == 7:
        # Icons row (small squares)
        for i in range(6):
            rect(20 + i * 28, 40, 18, 18)
    elif layout_id == 8:
        # Container border + inner content (padding candidates)
        rect(30, 30, 240, 160, thickness=3)
        rect(60, 60, 60, 30)
        rect(60, 110, 80, 30)
        rect(160, 60, 80, 80)
    elif layout_id == 9:
        # Three blocks with a large gap; adjacency should pick nearest only
        rect(20, 40, 40, 40)
        rect(90, 40, 40, 40)  # 30px gap from first
        rect(260, 40, 40, 40)  # far; should not be adjacent to first
    elif layout_id == 10:
        # Two stacked cards with internal content
        rect(20, 20, 260, 80, thickness=3)
        rect(40, 40, 80, 20)
        rect(40, 70, 120, 16)
        rect(20, 130, 260, 80, thickness=3)
        rect(40, 150, 100, 20)
        rect(40, 180, 140, 16)
    elif layout_id == 11:
        # Asymmetric padding, still yields padding min(x/y)
        rect(40, 40, 220, 140, thickness=3)
        rect(70, 70, 120, 30)
        rect(70, 120, 160, 30)
    else:  # pragma: no cover
        raise ValueError(layout_id)

    return canvas


@pytest.mark.skipif(cv2 is None, reason="opencv required")
def test_measurement_lane_stable_on_12_synthetic_images(monkeypatch):
    # Disable optional heavyweight detectors for deterministic CV-only smoke coverage.
    monkeypatch.setenv("FASTSAM_ENABLED", "0")
    monkeypatch.setenv("ENABLE_LAYOUTPARSER_TEXT", "0")
    monkeypatch.setenv("ENABLE_UIED", "0")

    extractor = CVSpacingExtractor(max_tokens=12, fastsam_enabled=False)
    seen_padding = 0
    seen_gaps = 0

    for layout_id in range(12):
        image_bytes = _encode_png(_make_layout(layout_id))
        result_a = extractor.extract_from_bytes(image_bytes)
        result_b = extractor.extract_from_bytes(image_bytes)

        candidates_a = getattr(result_a, "cv_distance_candidates", None) or []
        candidates_b = getattr(result_b, "cv_distance_candidates", None) or []

        # Deterministic output for identical inputs.
        assert candidates_a == candidates_b
        assert candidates_a, f"expected candidates for layout {layout_id}"

        # Validate schema and adjacency-dedup invariant.
        keys = set()
        for candidate in candidates_a:
            assert candidate["source"] in {"cv", "cv-adjacency"}
            assert candidate["type"] in {"gap", "padding"}
            assert candidate["axis"] in {"x", "y"}
            assert isinstance(candidate["distance_px"], int) and candidate["distance_px"] > 0
            assert isinstance(candidate["bbox_a"], list) and len(candidate["bbox_a"]) == 4
            assert isinstance(candidate["bbox_b"], list) and len(candidate["bbox_b"]) == 4
            assert 0.0 <= float(candidate["confidence"]) <= 1.0
            key = (
                candidate["type"],
                candidate["axis"],
                tuple(candidate["bbox_a"]),
                tuple(candidate["bbox_b"]),
            )
            assert key not in keys
            keys.add(key)

        seen_padding += sum(1 for c in candidates_a if c["type"] == "padding")
        seen_gaps += sum(1 for c in candidates_a if c["type"] == "gap")

    # Ensure we covered both candidate types across the suite.
    assert seen_gaps > 0
    assert seen_padding > 0
