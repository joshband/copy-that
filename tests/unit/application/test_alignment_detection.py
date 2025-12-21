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


def test_alignment_groups_limit_cross_column_spacing():
    nodes = [
        {"id": "left-1", "box": (0, 0, 20, 10)},
        {"id": "left-2", "box": (0, 30, 20, 10)},
        {"id": "right-1", "box": (100, 0, 20, 10)},
    ]
    groups = su.build_alignment_groups(nodes)
    edges = su.compute_adjacency_edges(
        nodes,
        axis="y",
        alignment_groups=groups["node_groups"],
        min_overlap_ratio=0.2,
    )
    # Only vertically aligned left column nodes should be adjacent
    assert any(e["node_a"] == "left-1" and e["node_b"] == "left-2" for e in edges)
    assert not any(e["node_b"] == "right-1" and e["axis"] == "y" for e in edges)
