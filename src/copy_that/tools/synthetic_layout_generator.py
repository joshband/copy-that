"""Deterministic synthetic layout generator for spacing evaluation."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from copy_that.application import spacing_utils as su


@dataclass(slots=True)
class SyntheticLayout:
    nodes: list[dict[str, Any]]
    expected_gaps: list[int]


def generate_grid_layout(rows: int, cols: int, cell_size: int, gap: int) -> SyntheticLayout:
    nodes: list[dict[str, Any]] = []
    for r in range(rows):
        for c in range(cols):
            x = c * (cell_size + gap)
            y = r * (cell_size + gap)
            nodes.append(
                {
                    "id": f"cell-{r}-{c}",
                    "box": [x, y, cell_size, cell_size],
                    "parent_id": None,
                    "children": [],
                }
            )
    expected = [gap]
    return SyntheticLayout(nodes=nodes, expected_gaps=expected)


def generate_stack(count: int, width: int, height: int, gap: int) -> SyntheticLayout:
    nodes: list[dict[str, Any]] = []
    for i in range(count):
        y = i * (height + gap)
        nodes.append(
            {"id": f"stack-{i}", "box": [0, y, width, height], "parent_id": None, "children": []}
        )
    return SyntheticLayout(nodes=nodes, expected_gaps=[gap])


def evaluate_spacing_accuracy(
    layout: SyntheticLayout,
    *,
    extractor: Callable[[Sequence[Mapping[str, Any]]], list[dict[str, Any]]] | None = None,
    tolerance: int = 1,
) -> dict[str, Any]:
    """
    Run a spacing extractor over a synthetic layout and compute accuracy.
    """
    extractor = extractor or (lambda nodes: su.extract_cv_distance_candidates(nodes))
    candidates = extractor(layout.nodes)
    gaps = [
        float(value)
        for value in (c.get("distance_px") for c in candidates if c.get("type") == "gap")
        if isinstance(value, (int, float))
    ]
    hit = 0
    for gap in gaps:
        if any(abs(int(gap) - exp) <= tolerance for exp in layout.expected_gaps):
            hit += 1
    precision = hit / max(len(gaps), 1)
    recall = min(1.0, hit / max(len(layout.expected_gaps), 1))
    return {
        "precision": precision,
        "recall": recall,
        "detected": sorted(set(int(g) for g in gaps)),
        "expected": layout.expected_gaps,
    }
