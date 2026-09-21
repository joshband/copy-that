"""Layout metrics for panel graphs."""

from __future__ import annotations

import statistics

from .layout_graph import PanelGraph


def size_variance(graph: PanelGraph) -> float:
    widths = [node.width for node in graph.nodes]
    return statistics.pvariance(widths) if len(widths) > 1 else 0.0


def gap_variance(graph: PanelGraph) -> float:
    gaps = []
    for row in graph.rows():
        row = sorted(row, key=lambda n: n.center_x)
        for left, right in zip(row, row[1:], strict=False):
            gaps.append(right.center_x - left.center_x)
    return statistics.pvariance(gaps) if len(gaps) > 1 else 0.0


def density(graph: PanelGraph) -> float:
    if not graph.nodes:
        return 0.0
    min_x = min(node.instance.bbox[0] for node in graph.nodes)
    min_y = min(node.instance.bbox[1] for node in graph.nodes)
    max_x = max(node.instance.bbox[0] + node.width for node in graph.nodes)
    max_y = max(node.instance.bbox[1] + node.height for node in graph.nodes)
    area = max((max_x - min_x) * (max_y - min_y), 1)
    return len(graph.nodes) / area


def regularity_score(graph: PanelGraph) -> float:
    row_centers = [sum(n.center_y for n in row) / len(row) for row in graph.rows() if row]
    row_var = statistics.pvariance(row_centers) if len(row_centers) > 1 else 0.0
    penalty = max(len(row_centers) - 1, 0) * 0.05
    return max(
        0.0,
        1.0 - (size_variance(graph) + gap_variance(graph) + row_var) / 1000.0 - penalty,
    )
