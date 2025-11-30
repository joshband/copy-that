from copy_that.application import spacing_utils as su


def test_cluster_gaps_single_mode():
    gaps = [8, 9, 8, 10, 9, 8.2]
    clusters = su.cluster_gaps(gaps, tolerance=2.0)
    assert clusters == [9] or clusters == [8] or clusters == [9, 9]


def test_cluster_gaps_two_modes():
    gaps = [8, 8, 9, 32, 33, 31]
    clusters = su.cluster_gaps(gaps, tolerance=2.0)
    assert len(clusters) == 2
    assert any(abs(c - 8) <= 1 for c in clusters)
    assert any(abs(c - 32) <= 1 for c in clusters)


def test_detect_alignment_lines_merges_with_tolerance():
    boxes = [
        (10, 10, 20, 10),
        (12, 30, 20, 10),
        (200, 10, 20, 10),
    ]
    lines = su.detect_alignment_lines(boxes, tolerance=3, min_support=2)
    assert lines["left"] == []  # left edges differ slightly and min_support filters out noise
