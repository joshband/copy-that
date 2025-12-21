from copy_that.application import spacing_utils as su


def test_compute_adjacency_edges_includes_depth_labels():
    nodes = [
        {"id": "a", "box": (0, 0, 10, 10)},
        {"id": "b", "box": (20, 0, 10, 10)},
    ]
    depth_lookup = {"a": 0.1, "b": 0.12}
    edges = su.compute_adjacency_edges(nodes, axis="x", depth_lookup=depth_lookup)
    assert edges, "Expected at least one adjacency edge"
    edge = edges[0]
    assert edge["depth_classification"] == "padding"
    assert edge["depth_delta"] is not None


def test_compute_adjacency_edges_flags_margin_on_depth_jump():
    nodes = [
        {"id": "a", "box": (0, 0, 10, 10)},
        {"id": "b", "box": (20, 0, 10, 10)},
    ]
    depth_lookup = {"a": 0.1, "b": 0.4}
    edges = su.compute_adjacency_edges(nodes, axis="x", depth_lookup=depth_lookup)
    assert edges
    assert edges[0]["depth_classification"] == "margin"
