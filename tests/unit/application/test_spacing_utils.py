"""Unit tests for spacing utility helpers."""

from copy_that.application import spacing_utils as su


def test_px_rem_roundtrip():
    assert su.px_to_rem(24) == 1.5
    assert su.rem_to_px(1.5) == 24
    assert su.px_to_em(8, context_size=16) == 0.5


def test_detect_base_unit_common_grids():
    assert su.detect_base_unit([8, 16, 24]) == 8
    assert su.detect_base_unit([4, 8, 12, 16]) == 4
    assert su.detect_base_unit([5, 10, 15]) == 5
    assert su.detect_base_unit([]) == 8  # default


def test_detect_scale_system_variants():
    assert su.detect_scale_system([4, 8, 12, 16]) == "4pt"
    assert su.detect_scale_system([8, 16, 24, 32]) == "8pt"
    assert su.detect_scale_system([1, 2, 3, 5, 8]) == "fibonacci"
    assert su.detect_scale_system([10, 15, 27]) == "custom"  # not a standard pattern


def test_detect_scale_position():
    values = [4, 8, 12, 16, 20]
    assert su.detect_scale_position(4, values) == 0
    assert su.detect_scale_position(16, values) == 3
    # nearest fit
    assert su.detect_scale_position(18, values) == 4
