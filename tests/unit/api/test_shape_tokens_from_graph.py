import pytest

spacing = pytest.importorskip("copy_that.interfaces.api.spacing")


def test_shape_tokens_from_graph_builds_radius_and_border_tokens():
    graph = [
        {
            "id": "1",
            "box": [0, 0, 10, 10],
            "meta": {"corner_radius": 6, "border_width": 2},
            "parent_id": None,
            "children": [],
        },
        {
            "id": "2",
            "box": [20, 0, 10, 10],
            "meta": {"corner_radius": 8},
            "parent_id": None,
            "children": [],
        },
    ]
    tokens = spacing._shape_tokens_from_graph(graph, namespace="token/test")  # type: ignore[attr-defined]
    ids = [t.id for t in tokens]
    assert "token/test/layout/radius/1" in ids
    assert "token/test/layout/border/1" in ids
