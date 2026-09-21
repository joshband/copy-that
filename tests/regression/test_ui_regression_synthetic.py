from copy_that.application import spacing_utils as su


def _boxes_row(
    count: int, start_x: int = 10, start_y: int = 10, w: int = 40, h: int = 20, gap: int = 10
):
    boxes = []
    x = start_x
    for _ in range(count):
        boxes.append((x, start_y, w, h))
        x += w + gap
    return boxes


def test_three_buttons_row_gap_cluster():
    boxes = _boxes_row(3, gap=10)
    graph = su.build_token_graph([{"index": idx, "box": b} for idx, b in enumerate(boxes)])
    # Gap clusters should include the consistent 10px gap
    assert graph
    gap_clusters = graph[0]["meta"]["gap_clusters"]
    assert 10 in gap_clusters["x"]


def test_containment_sets_parent_child():
    parent = {"index": 0, "box": (0, 0, 100, 100)}
    child = {"index": 1, "box": (10, 10, 20, 20)}
    graph = su.build_token_graph([parent, child])
    node_child = next(n for n in graph if n["id"] == "1")
    node_parent = next(n for n in graph if n["id"] == "0")
    assert node_child["parent_id"] == "0"
    assert "1" in node_parent["children"]


def test_overlapping_not_contained():
    a = {"index": 0, "box": (0, 0, 50, 50)}
    b = {"index": 1, "box": (30, 30, 30, 30)}  # partial overlap
    graph = su.build_token_graph([a, b])
    node_b = next(n for n in graph if n["id"] == "1")
    assert node_b["parent_id"] is None
