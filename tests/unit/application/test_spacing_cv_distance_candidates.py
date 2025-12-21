from copy_that.application import spacing_utils as su


def test_cv_candidates_only_use_adjacent_neighbors():
    token_graph = [
        {"id": "a", "box": (0, 0, 10, 10), "parent_id": None, "children": []},
        {"id": "b", "box": (20, 0, 10, 10), "parent_id": None, "children": []},
        {"id": "c", "box": (40, 0, 10, 10), "parent_id": None, "children": []},
    ]

    candidates = su.extract_cv_distance_candidates(token_graph)
    gaps_x = [c for c in candidates if c["type"] == "gap" and c["axis"] == "x"]

    assert len(gaps_x) == 2
    assert sorted(c["distance_px"] for c in gaps_x) == [10, 10]
    assert all(c["source"] == "cv-adjacency" for c in gaps_x)

    # Ensure we did not create a non-adjacent A->C measurement.
    assert not any(
        c["bbox_a"] == [0, 0, 10, 10] and c["bbox_b"] == [40, 0, 10, 10] for c in gaps_x
    )


def test_cv_candidates_preserve_adjacency_not_value():
    token_graph = [
        {"id": "a", "box": (0, 0, 40, 40), "parent_id": None, "children": []},
        {"id": "b", "box": (50, 0, 40, 40), "parent_id": None, "children": []},
        {"id": "c", "box": (0, 60, 40, 40), "parent_id": None, "children": []},
        {"id": "d", "box": (50, 60, 40, 40), "parent_id": None, "children": []},
    ]

    candidates = su.extract_cv_distance_candidates(token_graph)
    gaps = [c for c in candidates if c["type"] == "gap"]

    # Two distinct adjacency pairs can have the same distance; keep both.
    gaps_x = [c for c in gaps if c["axis"] == "x"]
    gaps_y = [c for c in gaps if c["axis"] == "y"]

    assert sorted(c["distance_px"] for c in gaps_x) == [10, 10]
    assert sorted(c["distance_px"] for c in gaps_y) == [20, 20]


def test_cv_candidates_emit_padding_from_container_to_content():
    token_graph = [
        {"id": "p", "box": (0, 0, 100, 100), "parent_id": None, "children": ["c1", "c2"]},
        {"id": "c1", "box": (10, 10, 20, 20), "parent_id": "p", "children": []},
        {"id": "c2", "box": (10, 40, 20, 20), "parent_id": "p", "children": []},
    ]

    candidates = su.extract_cv_distance_candidates(token_graph)
    padding = [c for c in candidates if c["type"] == "padding"]

    assert any(c["axis"] == "x" and c["distance_px"] == 10 for c in padding)
    assert any(c["axis"] == "y" and c["distance_px"] == 10 for c in padding)
    assert all(c["source"] == "cv" for c in padding)


def test_cv_candidates_include_node_ids_and_alignment_groups():
    token_graph = [
        {"id": "a", "box": (0, 0, 10, 10), "parent_id": None, "children": []},
        {"id": "b", "box": (20, 0, 10, 10), "parent_id": None, "children": []},
    ]
    candidates = su.extract_cv_distance_candidates(token_graph)
    gap = next(c for c in candidates if c["type"] == "gap")
    assert gap["node_a"] == "a"
    assert gap["node_b"] == "b"
    assert isinstance(gap.get("alignment_groups"), list)
