from copy_that.application import spacing_utils as su


def test_build_token_graph_assigns_parent():
    metrics = [
        {"index": 0, "box": (0, 0, 100, 100)},
        {"index": 1, "box": (10, 10, 20, 20)},
        {"index": 2, "box": (200, 0, 10, 10)},
    ]
    graph = su.build_token_graph(metrics)
    child = next(n for n in graph if n["id"] == "1")
    assert child["parent_id"] == "0"
    parent = next(n for n in graph if n["id"] == "0")
    assert "1" in parent["children"]


def test_build_token_graph_skips_overlaps():
    metrics = [
        {"index": 0, "box": (0, 0, 50, 50)},
        {"index": 1, "box": (30, 30, 30, 30)},  # partial overlap not full containment
    ]
    graph = su.build_token_graph(metrics)
    node = next(n for n in graph if n["id"] == "1")
    assert node["parent_id"] is None
