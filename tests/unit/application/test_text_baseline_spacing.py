from copy_that.application import spacing_utils as su


def test_detect_baseline_spacing_from_text_tokens():
    tokens = [
        {"id": "t1", "bbox": (0, 0, 10, 10)},
        {"id": "t2", "bbox": (0, 20, 10, 10)},
        {"id": "t3", "bbox": (0, 40, 10, 10)},
    ]
    spacing = su.detect_baseline_spacing_from_text_tokens(tokens)
    assert spacing is not None
    value, confidence = spacing
    assert value == 20
    assert confidence >= 0.9


def test_build_text_spacing_candidates_emits_pairs():
    tokens = [
        {"id": "a", "bbox": (0, 0, 10, 10)},
        {"id": "b", "bbox": (0, 18, 10, 10)},
    ]
    candidates = su.build_text_spacing_candidates(tokens, tolerance_px=3, min_pairs=1)
    assert len(candidates) == 1
    cand = candidates[0]
    assert cand["axis"] == "y"
    assert cand["node_a"] == "a"
    assert cand["node_b"] == "b"
    assert cand["source"] == "text-baseline"
