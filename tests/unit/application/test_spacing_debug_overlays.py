import pytest

np = pytest.importorskip("numpy")


def _import_spacing_deps():
    from copy_that.application.cv import spacing_cv_extractor
    from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor

    return spacing_cv_extractor, CVSpacingExtractor


def test_spacing_debug_payload_includes_toggles_and_confidence(monkeypatch):
    spacing_cv_extractor, CVSpacingExtractor = _import_spacing_deps()
    # Force simple deterministic geometry
    monkeypatch.setattr(
        spacing_cv_extractor,
        "preprocess_image",
        lambda data: {"cv_gray": np.zeros((8, 8), dtype=np.uint8)},
    )
    monkeypatch.setattr(
        spacing_cv_extractor, "components_to_bboxes", lambda gray: [(0, 0, 2, 2), (4, 0, 2, 2)]
    )
    monkeypatch.setattr(
        spacing_cv_extractor, "gaps_from_bboxes", lambda bboxes, **kwargs: ([4, 8], [])
    )
    monkeypatch.setattr(
        spacing_cv_extractor,
        "infer_grid_from_bboxes",
        lambda bboxes, canvas_width: {
            "columns": 2,
            "gutter_px": 4,
            "margin_left": 0,
            "margin_right": 0,
        },
    )
    monkeypatch.setattr(
        spacing_cv_extractor.su,
        "infer_base_spacing_robust",
        lambda gaps: (4, 0.9, [4, 8]),
    )
    monkeypatch.setattr(
        spacing_cv_extractor.su,
        "compute_spacing_confidence_breakdown",
        lambda candidates, base_unit, values: {"overall": 0.8, "measurement": 0.7},
    )
    monkeypatch.setattr(
        spacing_cv_extractor.su, "cross_check_gaps", lambda gaps, base_unit, **_: {}
    )
    monkeypatch.setattr(
        spacing_cv_extractor.su, "cluster_gaps", lambda gaps: {"dominant": gaps[:1]}
    )
    monkeypatch.setattr(spacing_cv_extractor, "run_layoutparser_text", lambda *_, **__: ([], []))
    monkeypatch.setattr(spacing_cv_extractor, "run_uied", lambda *_, **__: [])

    overlay_calls = []

    def fake_overlay(gray, bboxes, **kwargs):
        overlay_calls.append(kwargs)
        return "overlay-image"

    monkeypatch.setattr(spacing_cv_extractor, "generate_spacing_overlay", fake_overlay)

    extractor = CVSpacingExtractor(
        max_tokens=3,
        overlay_show_boxes=True,
        overlay_show_guides=False,
        overlay_show_baseline=True,
        overlay_show_grid=False,
    )
    result = extractor.extract_from_bytes(b"bytes")

    assert result.debug and result.debug["overlay_png_base64"] == "overlay-image"
    assert result.debug["overlays"] == {
        "boxes": True,
        "guides": False,
        "baseline": True,
        "grid": False,
    }
    assert result.debug["confidence_breakdown"]["overall"] == 0.8
    assert overlay_calls, "generate_spacing_overlay should be invoked"
    assert overlay_calls[0]["show_guides"] is False
    assert overlay_calls[0]["show_grid"] is False


def test_spacing_synthetic_layouts_produce_confidence(monkeypatch):
    spacing_cv_extractor, CVSpacingExtractor = _import_spacing_deps()
    layouts = {
        "card": ([(0, 0, 40, 30), (0, 50, 40, 30)], [20]),
        "table": ([(0, 0, 60, 20), (0, 32, 60, 20), (80, 0, 60, 20)], [12]),
        "dashboard": (
            [(0, 0, 80, 40), (90, 0, 80, 40), (0, 50, 170, 30)],
            [10, 12],
        ),
    }

    monkeypatch.setattr(
        spacing_cv_extractor,
        "preprocess_image",
        lambda data: {"cv_gray": np.zeros((120, 200), dtype=np.uint8)},
    )
    monkeypatch.setattr(spacing_cv_extractor, "run_layoutparser_text", lambda *_, **__: ([], []))
    monkeypatch.setattr(spacing_cv_extractor, "run_uied", lambda *_, **__: [])
    monkeypatch.setattr(spacing_cv_extractor, "generate_spacing_overlay", lambda *_, **__: None)
    monkeypatch.setattr(
        spacing_cv_extractor.su,
        "compute_spacing_confidence_breakdown",
        lambda candidates, base_unit, values: {"overall": 0.75, "measurement": 0.7},
    )

    for name, (boxes, gaps) in layouts.items():
        base = gaps[0]
        monkeypatch.setattr(spacing_cv_extractor, "components_to_bboxes", lambda gray, b=boxes: b)
        monkeypatch.setattr(
            spacing_cv_extractor, "gaps_from_bboxes", lambda *_, gaps=gaps: (gaps, [])
        )
        monkeypatch.setattr(
            spacing_cv_extractor.su,
            "infer_base_spacing_robust",
            lambda g=gaps, base=base: (base, 0.85, g),
        )
        monkeypatch.setattr(
            spacing_cv_extractor.su,
            "cross_check_gaps",
            lambda *_, base=base: {"dominant": base, "tolerance": 1.0},
        )
        monkeypatch.setattr(
            spacing_cv_extractor.su, "cluster_gaps", lambda gaps: {"dominant": gaps[:1]}
        )
        monkeypatch.setattr(
            spacing_cv_extractor,
            "infer_grid_from_bboxes",
            lambda *_: {"columns": 2, "confidence": 0.8},
        )

        extractor = CVSpacingExtractor(max_tokens=5, overlay_emit_debug=True)
        result = extractor.extract_from_bytes(f"{name}".encode())
        assert result.base_unit == base
        assert result.debug
        assert result.debug["confidence_breakdown"]["overall"] == 0.75
        assert result.tokens, f"{name} layout should yield tokens"
