import pytest

from copy_that.application import spacing_utils as su


def test_infer_base_spacing_robust_identifies_eight_point_grid():
    base, confidence, normalized = su.infer_base_spacing_robust([8, 16, 24, 32])
    assert base == 8
    assert confidence == pytest.approx(1.0)
    assert normalized == [8, 16, 24, 32]


def test_infer_base_spacing_robust_handles_noisy_values():
    base, confidence, normalized = su.infer_base_spacing_robust([8, 9, 16, 17, 30])
    assert base == 8
    assert 0.7 < confidence < 1.0
    assert normalized == [8, 16, 32]


def test_infer_base_spacing_robust_penalizes_unit_grids():
    base, confidence, normalized = su.infer_base_spacing_robust([8, 12, 20, 34, 47])
    assert base == 4
    assert confidence == pytest.approx(0.816, rel=1e-3)
    assert normalized[-1] >= normalized[0]


def test_infer_base_spacing_robust_uses_kde_peaks_for_noisy_data():
    base, confidence, normalized = su.infer_base_spacing_robust([7, 8, 9, 15, 16, 23, 31])
    assert base in {8, 4}
    assert confidence > 0.4
    assert all(v > 0 for v in normalized)


def test_infer_base_spacing_floors_sub_four_upload_surface_style():
    """High gap variance → raw GCD/min tends to 1px; prefer ≥4 design base."""
    # Upload-surface-style values from 2026-09-20 dogfood (plus tiny noise gaps)
    gaps = [15, 89, 172, 199, 363, 410, 1, 1, 2, 3]
    base, confidence, normalized = su.infer_base_spacing_robust(gaps)
    assert base >= 4
    # Must not advertise the old ~0.78 trust on a 1px noise base
    assert confidence < 0.75
    assert all(v >= base and v % base == 0 for v in normalized)


def test_infer_base_spacing_floors_pure_sub_four_noise():
    """When only sub-4 gaps exist, snap to 4 and cap confidence."""
    base, confidence, normalized = su.infer_base_spacing_robust([1, 1, 1, 2, 2, 3])
    assert base == 4
    assert confidence <= 0.25
    assert normalized == [4]
