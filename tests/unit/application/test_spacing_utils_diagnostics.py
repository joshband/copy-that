import pytest

from copy_that.application import spacing_utils as su


def test_compute_common_spacings_detects_repeated_vertical_gap():
    tokens = [
        {"box": (0, 0, 100, 40)},
        {"box": (0, 60, 100, 40)},
        {"box": (0, 120, 100, 40)},
    ]

    results = su.compute_common_spacings(tokens)

    assert results, "Expected at least one common spacing"
    top = results[0]
    assert top["value_px"] == 20
    assert top["orientation"] == "vertical"
    assert top["count"] >= 2


@pytest.mark.parametrize(
    "neighbor_gap",
    [24, 24.1, 23.6],
)
def test_compute_common_spacings_uses_neighbor_gap_hint(neighbor_gap: float):
    tokens = [
        {"box": (0, 0, 40, 40)},
        {"box": (100, 0, 40, 40), "neighbor_gap": neighbor_gap},
    ]

    results = su.compute_common_spacings(tokens, min_count=1)

    assert any(r["value_px"] == 24 for r in results)


def test_validate_extraction_warns_on_low_coverage_and_count():
    tokens = [{"box": (0, 0, 10, 10)}]
    result = su.validate_extraction(tokens, (200, 200), expected_types=["text"])
    assert result["warnings"]
    assert any("cover" in w.lower() for w in result["warnings"])
    assert any("text" in w.lower() for w in result["warnings"])


def test_validate_extraction_handles_missing_image():
    result = su.validate_extraction([], None)
    assert result["warnings"]
