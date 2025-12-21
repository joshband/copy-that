"""
Spacing Utility Functions

Utility functions for spacing calculations, scale detection, and grid compliance.
Follows the pattern of color_utils.py.
"""

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from collections.abc import Sequence as TypingSequence
from functools import reduce
from typing import Any, Iterable as TypingIterable, Literal

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore[assignment]

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore[assignment]

try:
    from copy_that.layoutlab.depth_estimator import (
        classify_spacing_depth,
        depth_scores_for_boxes,
        estimate_depth_map,
    )
except Exception:  # pragma: no cover - optional dependency
    classify_spacing_depth = None  # type: ignore[assignment]
    depth_scores_for_boxes = None  # type: ignore[assignment]
    estimate_depth_map = None  # type: ignore[assignment]


def px_to_rem(px_value: int, base_size: int = 16) -> float:
    """
    Convert pixels to rem units.

    Args:
        px_value: Value in pixels
        base_size: Base font size (default 16px)

    Returns:
        Value in rem units

    Example:
        >>> px_to_rem(24)
        1.5
        >>> px_to_rem(32, base_size=10)
        3.2
    """
    return round(px_value / base_size, 4)


def rem_to_px(rem_value: float, base_size: int = 16) -> int:
    """
    Convert rem units to pixels.

    Args:
        rem_value: Value in rem
        base_size: Base font size (default 16px)

    Returns:
        Value in pixels (rounded)
    """
    return round(rem_value * base_size)


def px_to_em(px_value: int, context_size: int = 16) -> float:
    """
    Convert pixels to em units (context-dependent).

    Args:
        px_value: Value in pixels
        context_size: Parent element font size

    Returns:
        Value in em units
    """
    return round(px_value / context_size, 4)


def detect_base_unit(spacing_values: list[int]) -> int:
    """
    Detect the base unit of a spacing scale using GCD analysis.

    Analyzes the greatest common divisor of spacing values to determine
    the fundamental unit (e.g., 4px for 4pt grid, 8px for 8pt grid).

    Args:
        spacing_values: List of spacing values in pixels

    Returns:
        Detected base unit in pixels

    Example:
        >>> detect_base_unit([8, 16, 24, 32])
        8
        >>> detect_base_unit([4, 8, 12, 16, 20])
        4
        >>> detect_base_unit([5, 10, 15, 20])
        5
    """
    if not spacing_values:
        return 8  # Default to 8pt grid

    # Filter out zeros and get unique values
    values = list(set(v for v in spacing_values if v > 0))

    if len(values) == 1:
        # Single value - return it if common grid unit, else find factor
        value = values[0]
        if value % 8 == 0:
            return 8
        elif value % 4 == 0:
            return 4
        return value

    # Calculate GCD of all values
    def gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    base = reduce(gcd, values)

    # Prefer common grid systems
    if base >= 8 and base % 8 == 0:
        return 8
    elif base >= 4 and base % 4 == 0:
        return 4

    return base if base > 0 else 8


def _kde_peaks(values: Sequence[int]) -> list[int]:
    """Estimate dominant spacing peaks using KDE (scipy or sklearn)."""
    if np is None:  # numpy unavailable in lightweight environments
        return []
    if len(values) < 2:
        return []
    vals = np.array(sorted(values), dtype=float)
    if vals.size < 2:
        return []
    bandwidth = max(float(np.std(vals)) * 0.2, 1.0)
    density_fn = None
    grid: np.ndarray
    try:
        from scipy.stats import gaussian_kde  # type: ignore

        density_fn = gaussian_kde(vals, bw_method=bandwidth / max(vals.ptp(), 1.0))
    except Exception:
        try:
            from sklearn.neighbors import KernelDensity  # type: ignore

            density_fn = KernelDensity(bandwidth=bandwidth, kernel="gaussian").fit(
                vals.reshape(-1, 1)
            )
        except Exception:
            return []
    grid = np.linspace(float(vals.min()), float(vals.max()), num=int(min(256, max(vals.ptp(), 8))))
    if grid.size < 3 or density_fn is None:
        return []
    try:
        if hasattr(density_fn, "evaluate"):
            densities = density_fn.evaluate(grid)
        else:
            densities = np.exp(density_fn.score_samples(grid.reshape(-1, 1)))  # type: ignore[arg-type]
    except Exception:
        return []
    peaks: list[int] = []
    for i in range(1, len(grid) - 1):
        if densities[i] >= densities[i - 1] and densities[i] >= densities[i + 1]:
            peaks.append(int(round(grid[i])))
    return sorted({p for p in peaks if p > 0})


def infer_base_spacing_robust(
    spacing_values: Sequence[float], tolerance_px: float = 1.0
) -> tuple[int, float, list[int]]:
    """Infer base unit, confidence, and normalized spacings from raw gaps."""

    values = [int(round(v)) for v in spacing_values if v and v > 0]
    if not values:
        return 8, 0.0, []

    counts = Counter(values)
    total = sum(counts.values()) or 1
    unique = sorted(counts)
    diffs = [unique[i + 1] - unique[i] for i in range(len(unique) - 1) if unique[i + 1] > unique[i]]

    candidates: set[int] = {min(unique), detect_base_unit(values)}
    mode_val = counts.most_common(1)[0][0]
    candidates.add(mode_val)
    if diffs:
        candidates.add(min(diffs))
        diff_mode = Counter(diffs).most_common(1)[0][0]
        candidates.add(diff_mode)
    kde_peaks = _kde_peaks(values)
    candidates.update(kde_peaks)
    if np is None:
        candidates.update({4, 8})

    candidates = {max(1, int(c)) for c in candidates if c}

    def score(base: int) -> float:
        if base <= 0:
            return 0.0
        aligned = 0
        for val, freq in counts.items():
            multiple = max(1, int(round(val / base)))
            snapped = multiple * base
            if abs(val - snapped) <= tolerance_px:
                aligned += freq
        coverage = aligned / total
        bonus = 1.0
        if base == 8:
            bonus = 1.05
        elif base == 4:
            bonus = 1.02
        if kde_peaks and np is not None and any(abs(base - peak) <= 1 for peak in kde_peaks):
            bonus += 0.05
        bias = 1.0
        if base <= 2:
            bias = 0.35
        elif base == 3:
            bias = 0.5
        return coverage * bonus * bias

    scored = [(cand, score(cand)) for cand in candidates]
    scored.sort(key=lambda item: (item[1], -(abs(item[0] - 8)), -item[0]), reverse=True)
    best_base, best_score = scored[0]

    normalized = sorted(
        {max(best_base, int(max(1, round(val / best_base)) * best_base)) for val in values}
    )

    return best_base, round(min(1.0, best_score), 4), normalized


def infer_base_spacing(spacing_values: list[int]) -> tuple[int, float]:
    """Backward compatible wrapper around :func:`infer_base_spacing_robust`."""

    base, confidence, _ = infer_base_spacing_robust(spacing_values)
    return base, confidence


def compare_base_units(
    expected: int | float | None, inferred: int | float | None, tolerance: int | float = 1
) -> dict[str, Any]:
    """
    Compare expected vs inferred spacing bases with a tolerance.
    """
    if expected is None or inferred is None:
        return {
            "expected": expected,
            "inferred": inferred,
            "within_tolerance": True,
            "delta": None,
            "mode": "no-expected",
        }
    delta = float(inferred) - float(expected)
    within = abs(delta) <= float(tolerance)
    return {
        "expected": float(expected),
        "inferred": float(inferred),
        "within_tolerance": within,
        "delta": delta,
        "mode": "match" if within else "mismatch",
    }


def cross_check_gaps(
    gaps: Sequence[float], base_unit: float, tolerance_px: float = 1.0
) -> dict[str, Any]:
    """
    Compare dominant CV gaps to a base spacing with ±tolerance.
    """
    if not gaps or base_unit <= 0:
        return {}
    counts = Counter(int(round(g)) for g in gaps)
    dominant_gap, _ = counts.most_common(1)[0]
    deviation = abs(dominant_gap - base_unit)
    aligned = deviation <= tolerance_px
    return {
        "dominant_gap": float(dominant_gap),
        "base_unit": float(base_unit),
        "tolerance_px": float(tolerance_px),
        "aligned": aligned,
        "deviation_px": float(deviation),
    }


def compute_common_spacings(
    tokens: TypingSequence[Any],
    min_count: int = 2,
    tolerance_px: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Compute frequently occurring spacing values between adjacent elements.

    The function expects each token to carry a bounding box under ``box`` or ``bbox``
    in the form ``(x, y, width, height)``. It will:
      - measure horizontal gaps when elements share vertical overlap
      - measure vertical gaps when elements share horizontal overlap
      - include ``neighbor_gap`` hints when present on the token
      - aggregate values within ``tolerance_px`` using rounded pixel distances

    Args:
        tokens: Sequence of tokens or dicts with bounding box data.
        min_count: Minimum occurrences required for a spacing value to be returned.
        tolerance_px: Maximum delta when grouping gaps of the same nominal size.

    Returns:
        A list of dicts: ``{"value_px": <int>, "count": <int>, "orientation": "horizontal"|"vertical"|"mixed"}``
        sorted by frequency (descending).
    """

    def _extract_box(item: Any) -> tuple[int, int, int, int] | None:
        candidate: Any | None = None
        if isinstance(item, Mapping):
            candidate = item.get("box") or item.get("bbox")
        elif hasattr(item, "box"):
            candidate = item.box
        elif hasattr(item, "bbox"):
            candidate = item.bbox
        else:
            candidate = item
        if candidate is None:
            return None
        try:
            x, y, w, h = candidate  # type: ignore[misc]
            return (
                int(round(float(x))),
                int(round(float(y))),
                int(round(float(w))),
                int(round(float(h))),
            )
        except Exception:
            return None

    boxes: list[tuple[int, int, int, int]] = []
    ids: list[str] = []
    neighbor_gaps: list[float] = []
    for idx, tok in enumerate(tokens):
        box = _extract_box(tok)
        if box:
            boxes.append(box)
            ids.append(str(getattr(tok, "id", None) or getattr(tok, "index", None) or idx))
        if isinstance(tok, Mapping):
            gap_hint = tok.get("neighbor_gap")
            if gap_hint is not None:
                try:
                    neighbor_gaps.append(float(gap_hint))
                except Exception:
                    continue

    if not boxes and not neighbor_gaps:
        return []

    orientation_counts: MutableMapping[int, dict[str, int]] = defaultdict(
        lambda: {"horizontal": 0, "vertical": 0, "mixed": 0}
    )
    gap_counter: Counter[int] = Counter()

    nodes = [{"id": ids[i], "box": box} for i, box in enumerate(boxes)]
    alignment_graph = build_alignment_groups(nodes)

    def _tally(edges: list[dict[str, Any]]) -> None:
        for edge in edges:
            rounded = int(round(edge["distance_px"]))
            gap_counter[rounded] += 1
            orient_key = "horizontal" if edge["axis"] == "x" else "vertical"
            orientation_counts[rounded][orient_key] += 1

    for axis in ("x", "y"):
        edges = compute_adjacency_edges(
            nodes,
            axis=axis,  # type: ignore[arg-type]
            min_overlap_ratio=0.25,
            alignment_groups=alignment_graph["node_groups"],
        )
        _tally(edges)

    # Include neighbor_gap hints (orientation unknown)
    for gap in neighbor_gaps:
        rounded = int(round(gap))
        gap_counter[rounded] += 1
        orientation_counts[rounded]["mixed"] += 1

    if not gap_counter:
        return []

    def _dominant_orientation(counts: dict[str, int]) -> str:
        horiz = counts.get("horizontal", 0)
        vert = counts.get("vertical", 0)
        mixed = counts.get("mixed", 0)
        if mixed and max(horiz, vert) <= mixed:
            return "mixed"
        if horiz and vert and abs(horiz - vert) <= 1:
            return "mixed"
        return "horizontal" if horiz >= vert else "vertical"

    results: list[dict[str, Any]] = []
    for value, count in gap_counter.most_common():
        if count < min_count:
            continue
        orient = _dominant_orientation(orientation_counts[value])
        results.append({"value_px": int(value), "count": int(count), "orientation": orient})

    # If everything was below the threshold, surface the strongest signal
    if not results and gap_counter:
        value, count = gap_counter.most_common(1)[0]
        orient = _dominant_orientation(orientation_counts[value])
        results.append({"value_px": int(value), "count": int(count), "orientation": orient})

    return results


Axis = Literal["x", "y"]


def extract_cv_distance_candidates(
    token_graph: Sequence[Mapping[str, Any]] | None,
    *,
    canvas_size: tuple[int, int] | None = None,
    min_overlap_ratio: float = 0.3,
    min_box_area: int = 32,
    max_box_area_ratio: float = 0.97,
    depth_lookup: Mapping[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Extract raw spacing candidates (gaps + padding) from CV token graph geometry.

    The output is intentionally "pre-semantic": it contains only pixel distances between
    adjacent elements (gaps) and inner distances from container-to-content (padding),
    with no LLM/AI classification.

    Args:
        token_graph: Output from :func:`build_token_graph` (nodes with ``box``, ``parent_id``, ``children``).
        canvas_size: Optional (width, height) for filtering giant background boxes.
        min_overlap_ratio: Minimum overlap ratio (orthogonal axis) to consider boxes adjacent.
        min_box_area: Minimum bbox area in pixels to include.
        max_box_area_ratio: Maximum bbox area ratio vs canvas area to include when canvas_size is provided.

    Returns:
        List of candidates:
        {
          "distance_px": int,
          "axis": "x" | "y",
          "type": "gap" | "padding",
          "bbox_a": [x, y, w, h],
          "bbox_b": [x, y, w, h],
          "confidence": float,
          "source": "cv-adjacency" | "cv",
          "node_a": str | None,
          "node_b": str | None,
        }
    """

    if not token_graph:
        return []

    def _as_bbox(raw: Any) -> tuple[int, int, int, int] | None:
        if raw is None:
            return None
        try:
            x, y, w, h = raw  # type: ignore[misc]
            box = (
                int(round(float(x))),
                int(round(float(y))),
                int(round(float(w))),
                int(round(float(h))),
            )
        except Exception:
            return None
        if box[2] <= 0 or box[3] <= 0:
            return None
        return box

    def _area(box: tuple[int, int, int, int]) -> int:
        return max(int(box[2]) * int(box[3]), 0)

    canvas_area = None
    if canvas_size:
        canvas_area = max(int(canvas_size[0]) * int(canvas_size[1]), 1)

    nodes: list[dict[str, Any]] = []
    for idx, raw_node in enumerate(token_graph):
        box = _as_bbox(raw_node.get("box") or raw_node.get("bbox"))
        if not box:
            continue
        area = _area(box)
        if area < min_box_area:
            continue
        if canvas_area is not None and (area / canvas_area) > max_box_area_ratio:
            continue
        raw_id = raw_node.get("id")
        node_id = str(raw_id) if raw_id not in {None, ""} else f"node-{idx}"
        nodes.append(
            {
                "id": node_id,
                "parent_id": raw_node.get("parent_id"),
                "children": list(raw_node.get("children") or []),
                "box": box,
            }
        )

    if len(nodes) < 2:
        return []

    id_to_box: dict[str, tuple[int, int, int, int]] = {n["id"]: n["box"] for n in nodes}

    def _clamp01(val: float) -> float:
        return max(0.0, min(1.0, val))

    def _candidate_key(c: dict[str, Any]) -> tuple[Any, ...]:
        return (
            c.get("type"),
            c.get("axis"),
            tuple(c.get("bbox_a") or ()),
            tuple(c.get("bbox_b") or ()),
            c.get("node_a"),
            c.get("node_b"),
        )

    def _add_candidate(
        dest: dict[tuple[Any, ...], dict[str, Any]],
        *,
        distance_px: int,
        axis: Axis,
        kind: str,
        bbox_a: tuple[int, int, int, int],
        bbox_b: tuple[int, int, int, int],
        confidence: float,
        node_a: str | None = None,
        node_b: str | None = None,
        alignment_groups: Sequence[str] | None = None,
        depth_classification: str | None = None,
        depth_delta: float | None = None,
    ) -> None:
        if distance_px <= 0:
            return
        candidate = {
            "distance_px": int(distance_px),
            "axis": axis,
            "type": kind,
            "bbox_a": [int(v) for v in bbox_a],
            "bbox_b": [int(v) for v in bbox_b],
            "confidence": round(_clamp01(float(confidence)), 4),
            "source": "cv-adjacency" if kind == "gap" else "cv",
            "node_a": node_a,
            "node_b": node_b,
            "alignment_groups": list(alignment_groups) if alignment_groups else [],
            "depth_classification": depth_classification,
            "depth_delta": depth_delta,
        }
        key = _candidate_key(candidate)
        existing = dest.get(key)
        if existing is None or float(candidate["confidence"]) > float(
            existing.get("confidence", 0.0)
        ):
            dest[key] = candidate

    best_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}

    # Gap candidates: compute adjacency among siblings (same parent_id), plus root-level adjacency.
    groups: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        groups[node.get("parent_id")].append(node)

    alignment_graph = build_alignment_groups(nodes)

    for group_nodes in groups.values():
        if len(group_nodes) < 2:
            continue
        for axis in ("x", "y"):
            edges = compute_adjacency_edges(
                group_nodes,
                axis=axis,  # type: ignore[arg-type]
                min_overlap_ratio=min_overlap_ratio,
                alignment_groups=alignment_graph["node_groups"],
                depth_lookup=depth_lookup,
            )
            for edge in edges:
                conf = 0.25 + 0.75 * float(edge["overlap_ratio"])
                _add_candidate(
                    best_by_key,
                    distance_px=int(edge["distance_px"]),
                    axis=axis,  # type: ignore[arg-type]
                    kind="gap",
                    bbox_a=tuple(edge["bbox_a"]),
                    bbox_b=tuple(edge["bbox_b"]),
                    confidence=conf,
                    node_a=edge.get("node_a"),
                    node_b=edge.get("node_b"),
                    alignment_groups=edge.get("alignment_groups"),
                    depth_classification=edge.get("depth_classification"),
                    depth_delta=edge.get("depth_delta"),
                )

    # Padding candidates: for each container with children, measure container-to-content inset.
    for node in nodes:
        children = node.get("children") or []
        if not children:
            continue
        child_boxes = [id_to_box.get(str(cid)) for cid in children]
        child_boxes = [b for b in child_boxes if b]
        if not child_boxes:
            continue

        parent = node["box"]
        px, py, pw, ph = parent
        px2, py2 = px + pw, py + ph
        cx1 = min(b[0] for b in child_boxes)
        cy1 = min(b[1] for b in child_boxes)
        cx2 = max(b[0] + b[2] for b in child_boxes)
        cy2 = max(b[1] + b[3] for b in child_boxes)
        content = (int(cx1), int(cy1), int(cx2 - cx1), int(cy2 - cy1))

        # Content must be inside parent to be a padding candidate.
        if cx1 < px or cy1 < py or cx2 > px2 or cy2 > py2:
            continue

        left = cx1 - px
        right = px2 - cx2
        top = cy1 - py
        bottom = py2 - cy2

        pad_x = min(left, right)
        pad_y = min(top, bottom)
        if pad_x <= 0 and pad_y <= 0:
            continue

        parent_area = float(_area(parent) or 1)
        coverage = min(1.0, float(sum(_area(b) for b in child_boxes)) / parent_area)
        conf = 0.3 + 0.7 * coverage

        if pad_x > 0:
            _add_candidate(
                best_by_key,
                distance_px=int(pad_x),
                axis="x",
                kind="padding",
                bbox_a=parent,
                bbox_b=content,
                confidence=conf,
            )
        if pad_y > 0:
            _add_candidate(
                best_by_key,
                distance_px=int(pad_y),
                axis="y",
                kind="padding",
                bbox_a=parent,
                bbox_b=content,
                confidence=conf,
            )

    candidates = list(best_by_key.values())
    candidates.sort(
        key=lambda c: (
            str(c.get("type")),
            str(c.get("axis")),
            int(c.get("distance_px") or 0),
            tuple(c.get("bbox_a") or ()),
            tuple(c.get("bbox_b") or ()),
        )
    )
    return candidates


def cluster_gaps(values: Sequence[float], tolerance: float = 2.5) -> list[int]:
    """
    Cluster numeric gap values within a tolerance and return cluster centroids.

    Args:
        values: Gap values (pixels)
        tolerance: Max difference to consider values in the same cluster

    Returns:
        Sorted list of cluster centers (ints)
    """
    vals = sorted(int(round(v)) for v in values if v is not None)
    if not vals:
        return []
    clusters: list[list[int]] = [[vals[0]]]
    for v in vals[1:]:
        if abs(v - clusters[-1][-1]) <= tolerance:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    centers = [int(round(sum(c) / len(c))) for c in clusters]
    return sorted(centers)


def compute_spacing_confidence_breakdown(
    candidates: Sequence[Mapping[str, Any]] | None,
    base_unit: int | None,
    normalized_values: Sequence[int] | None = None,
) -> dict[str, float]:
    """Build interpretable confidence components for spacing inference."""

    candidates = candidates or []
    normalized_values = normalized_values or []

    measurement_confidence = max(0.1, min(1.0, len(candidates) / 12.0))

    if base_unit and base_unit > 0 and normalized_values:
        aligned = sum(1 for v in normalized_values if v % base_unit <= 1 or base_unit - (v % base_unit) <= 1)
        grid_confidence = aligned / max(len(normalized_values), 1)
    else:
        grid_confidence = 0.25

    semantic_confidence = 0.25
    if candidates:
        aligned_edges = [
            c for c in candidates if (c.get("alignment_groups") or c.get("source") == "cv-adjacency")
        ]
        semantic_confidence = max(0.25, min(1.0, len(aligned_edges) / max(len(candidates), 1)))

    overall = round(
        0.5 * measurement_confidence + 0.3 * grid_confidence + 0.2 * semantic_confidence, 4
    )

    return {
        "measurement_confidence": round(float(measurement_confidence), 4),
        "grid_confidence": round(float(grid_confidence), 4),
        "semantic_confidence": round(float(semantic_confidence), 4),
        "overall": overall,
    }


def infer_grid_from_components(
    bboxes: Sequence[tuple[int, int, int, int]],
    *,
    canvas_width: int | None = None,
    guides: Sequence[int] | None = None,
) -> dict[str, Any]:
    """
    Lightweight grid inference using component positions and optional guide lines.
    Returns columns, gutter_px, margin_left, margin_right when inferable.
    """
    if not bboxes:
        return {}
    xs = sorted((x for x, _, _, _ in bboxes))
    widths = [w for _, _, w, _ in bboxes if w > 0]
    if not xs or not widths:
        return {}

    # Margins from extremes if canvas width known
    margin_left = xs[0] if canvas_width else None
    margin_right = None
    if canvas_width:
        max_x = max(x + w for x, _, w, _ in bboxes)
        margin_right = max(canvas_width - max_x, 0)

    # Gutter from x gaps
    gaps = []
    sorted_boxes = sorted(bboxes, key=lambda b: b[0])
    for i in range(len(sorted_boxes) - 1):
        x1, _, w1, _ = sorted_boxes[i]
        x2, _, _, _ = sorted_boxes[i + 1]
        gap = x2 - (x1 + w1)
        if gap > 0:
            gaps.append(gap)
    gutter_px = cluster_gaps(gaps, tolerance=1.5)[0] if gaps else None

    # Columns: use guide count or approximate via average width + gutter
    columns = None
    if guides and len(guides) > 1:
        columns = len(guides) - 1
    else:
        avg_width = sum(widths) / max(len(widths), 1)
        if gutter_px and canvas_width:
            usable = canvas_width - (margin_left or 0) - (margin_right or 0) + gutter_px
            approx_cols = usable / max(avg_width + gutter_px, 1)
            columns = max(1, min(24, int(round(approx_cols))))
    result = {}
    if columns:
        result["columns"] = int(columns)
    if gutter_px:
        result["gutter_px"] = int(gutter_px)
    if margin_left is not None:
        result["margin_left"] = int(margin_left)
    if margin_right is not None:
        result["margin_right"] = int(margin_right)
    return result


def detect_alignment_lines(
    boxes: Sequence[tuple[int, int, int, int]],
    tolerance: int = 3,
    min_support: int = 2,
) -> dict[str, list[int]]:
    """
    Detect common vertical/horizontal alignment lines from bounding boxes.

    Args:
        boxes: List of (x, y, w, h)
        tolerance: Pixel tolerance to merge lines
        min_support: Minimum boxes sharing a line to include it

    Returns:
        dict with keys: left, right, center_x, top, bottom, center_y
    """
    if not boxes:
        return {k: [] for k in ["left", "right", "center_x", "top", "bottom", "center_y"]}

    def _merge_positions(positions: list[int]) -> list[int]:
        positions = sorted(positions)
        if not positions:
            return []
        merged = [positions[0]]
        for pos in positions[1:]:
            if abs(pos - merged[-1]) <= tolerance:
                merged[-1] = int(round((merged[-1] + pos) / 2))
            else:
                merged.append(pos)
        return merged

    lefts = []
    rights = []
    centers_x = []
    tops = []
    bottoms = []
    centers_y = []
    for x, y, w, h in boxes:
        lefts.append(x)
        rights.append(x + w)
        centers_x.append(x + w // 2)
        tops.append(y)
        bottoms.append(y + h)
        centers_y.append(y + h // 2)

    def _filter_support(vals: list[int]) -> list[int]:
        counts = Counter(vals)
        return sorted([v for v, c in counts.items() if c >= min_support])

    def _supported_and_merged(vals: list[int]) -> list[int]:
        filtered = _filter_support(vals)
        return _merge_positions(filtered)

    return {
        "left": _supported_and_merged(lefts),
        "right": _supported_and_merged(rights),
        "center_x": _supported_and_merged(centers_x),
        "top": _supported_and_merged(tops),
        "bottom": _supported_and_merged(bottoms),
        "center_y": _supported_and_merged(centers_y),
    }


def build_alignment_groups(
    nodes: TypingIterable[Mapping[str, Any]],
    tolerance: int = 3,
    min_support: int = 2,
) -> dict[str, dict[str, set[str]]]:
    """
    Construct an alignment constraint graph over nodes.

    Returns:
        {"node_groups": {node_id: {group_ids}}, "groups": {group_id: {node_ids}}}
    """

    items: list[tuple[str, tuple[int, int, int, int]]] = []
    for node in nodes:
        node_id = str(node.get("id"))
        box = node.get("box") or node.get("bbox")
        if not box or len(box) != 4:
            continue
        items.append((node_id, tuple(int(v) for v in box)))  # type: ignore[arg-type]

    if not items:
        return {"node_groups": {}, "groups": {}}

    boxes = [b for _, b in items]
    align_lines = detect_alignment_lines(boxes, tolerance=tolerance, min_support=min_support)
    group_map: dict[str, set[str]] = defaultdict(set)
    node_groups: dict[str, set[str]] = defaultdict(set)

    def _assign(node_id: str, key: str) -> None:
        group_map[key].add(node_id)
        node_groups[node_id].add(key)

    for node_id, box in items:
        x, y, w, h = box
        left, right = x, x + w
        top, bottom = y, y + h
        center_x = x + w // 2
        center_y = y + h // 2
        for pos in align_lines["left"]:
            if abs(left - pos) <= tolerance:
                _assign(node_id, f"x:left:{pos}")
        for pos in align_lines["right"]:
            if abs(right - pos) <= tolerance:
                _assign(node_id, f"x:right:{pos}")
        for pos in align_lines["center_x"]:
            if abs(center_x - pos) <= tolerance:
                _assign(node_id, f"x:center:{pos}")
        for pos in align_lines["top"]:
            if abs(top - pos) <= tolerance:
                _assign(node_id, f"y:top:{pos}")
        for pos in align_lines["bottom"]:
            if abs(bottom - pos) <= tolerance:
                _assign(node_id, f"y:bottom:{pos}")
        for pos in align_lines["center_y"]:
            if abs(center_y - pos) <= tolerance:
                _assign(node_id, f"y:center:{pos}")

    return {"node_groups": dict(node_groups), "groups": dict(group_map)}


def compute_adjacency_edges(
    nodes: TypingIterable[Mapping[str, Any]],
    *,
    axis: Axis,
    min_overlap_ratio: float = 0.3,
    alignment_groups: Mapping[str, set[str]] | None = None,
    depth_lookup: Mapping[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Compute true neighbor adjacency using a sweep along the given axis."""

    def _overlap_ratio(
        a: tuple[int, int, int, int], b: tuple[int, int, int, int], axis: Axis
    ) -> float:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        ax2, ay2 = ax + aw, ay + ah
        bx2, by2 = bx + bw, by + bh
        if axis == "x":
            overlap = min(ay2, by2) - max(ay, by)
            denom = min(ah, bh)
        else:
            overlap = min(ax2, bx2) - max(ax, bx)
            denom = min(aw, bw)
        if denom <= 0:
            return 0.0
        return max(0.0, float(overlap) / float(denom))

    items: list[tuple[str, tuple[int, int, int, int]]] = []
    for node in nodes:
        nid = str(node.get("id"))
        box = node.get("box") or node.get("bbox")
        if not box or len(box) != 4:
            continue
        items.append((nid, tuple(int(v) for v in box)))  # type: ignore[arg-type]

    if len(items) < 2:
        return []

    idx_start = 0 if axis == "x" else 1
    idx_size = 2 if axis == "x" else 3
    sorted_items = sorted(
        items, key=lambda pair: (pair[1][idx_start], pair[1][1 if axis == "x" else 0])
    )

    edges: list[dict[str, Any]] = []
    for i, (nid, box) in enumerate(sorted_items):
        start = box[idx_start]
        size = box[idx_size]
        end = start + size
        orth_start = box[1 if axis == "x" else 0]
        orth_size = box[3 if axis == "x" else 2]
        orth_end = orth_start + orth_size
        best: tuple[float, tuple[str, tuple[int, int, int, int]], float] | None = None
        for j in range(i - 1, -1, -1):
            pid, pbox = sorted_items[j]
            p_start = pbox[idx_start]
            p_size = pbox[idx_size]
            p_end = p_start + p_size
            gap = start - p_end
            if gap <= 0:
                continue
            overlap = _overlap_ratio(box, pbox, axis)
            if overlap < min_overlap_ratio:
                continue
            if alignment_groups is not None:
                g_a = alignment_groups.get(nid, set())
                g_b = alignment_groups.get(pid, set())
                if g_a and g_b and not (g_a & g_b):
                    continue
            # orthogonal occlusion check: ensure no intervening box lies between p_end and start
            if best is None or gap < best[0] or (gap == best[0] and overlap > best[2]):
                best = (gap, (pid, pbox), overlap)
        if best:
            gap_px, (pid, pbox), overlap = best
            shared = (
                list(sorted(alignment_groups.get(nid, set()) & alignment_groups.get(pid, set())))
                if alignment_groups is not None
                else []
            )
            depth_classification = None
            depth_delta = None
            if depth_lookup is not None and classify_spacing_depth is not None:
                depth_classification = (
                    "padding" if abs(depth_lookup.get(pid, 0.5) - depth_lookup.get(nid, 0.5)) <= 0.08 else "margin"
                )
                depth_delta = abs(depth_lookup.get(pid, 0.5) - depth_lookup.get(nid, 0.5))
            edges.append(
                {
                    "node_a": pid,
                    "node_b": nid,
                    "axis": axis,
                    "distance_px": int(round(gap_px)),
                    "overlap_ratio": float(overlap),
                    "bbox_a": list(pbox),
                    "bbox_b": list(box),
                    "alignment_groups": shared,
                    "depth_classification": depth_classification,
                    "depth_delta": depth_delta,
                }
            )
    return edges


def build_depth_lookup(
    nodes: TypingIterable[Mapping[str, Any]], depth_map: Any | None
) -> dict[str, float]:
    """Compute average depth per node bounding box."""
    if depth_scores_for_boxes is None:
        return {}
    boxes: list[tuple[int, int, int, int]] = []
    ids: list[str] = []
    for node in nodes:
        nid = str(node.get("id"))
        box = node.get("box") or node.get("bbox")
        if not box or len(box) != 4:
            continue
        boxes.append(tuple(int(v) for v in box))  # type: ignore[arg-type]
        ids.append(nid)
    scores = depth_scores_for_boxes(boxes, depth_map)
    return {ids[i]: scores[i] for i in range(len(ids))}


def _box_area(box: tuple[int, int, int, int]) -> int:
    _, _, w, h = box
    return max(int(w) * int(h), 0)


def _box_contains(
    outer: tuple[int, int, int, int],
    inner: tuple[int, int, int, int],
    tolerance: int = 2,
    min_coverage: float = 0.9,
) -> bool:
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    if iw <= 0 or ih <= 0 or ow <= 0 or oh <= 0:
        return False
    ox2, oy2 = ox + ow, oy + oh
    ix2, iy2 = ix + iw, iy + ih
    if (
        ix >= ox - tolerance
        and iy >= oy - tolerance
        and ix2 <= ox2 + tolerance
        and iy2 <= oy2 + tolerance
    ):
        return True
    inter_left = max(ox, ix)
    inter_top = max(oy, iy)
    inter_right = min(ox2, ix2)
    inter_bottom = min(oy2, iy2)
    if inter_right <= inter_left or inter_bottom <= inter_top:
        return False
    inter_area = (inter_right - inter_left) * (inter_bottom - inter_top)
    inner_area = iw * ih
    return inter_area / max(inner_area, 1) >= min_coverage


def _polygon_bbox(poly: Sequence[Sequence[int]] | None) -> tuple[int, int, int, int] | None:
    if not poly:
        return None
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return (int(min_x), int(min_y), int(max_x - min_x), int(max_y - min_y))


def _poly_contains(
    outer: Sequence[Sequence[int]] | None,
    inner: Sequence[Sequence[int]] | None,
    tolerance: int = 2,
    min_coverage: float = 0.7,
) -> bool:
    if np is None:
        return False
    if not outer or not inner:
        return False
    if len(inner) < 3 or len(outer) < 3:
        return False
    try:
        if cv2 is None:
            return False
        outer_arr = np.array(outer, dtype=np.int32)
        inner_arr = np.array(inner, dtype=np.int32)
        # Quick bbox reject
        outer_box = _polygon_bbox(outer)
        inner_box = _polygon_bbox(inner)
        if (
            outer_box
            and inner_box
            and not _box_contains(
                outer_box, inner_box, tolerance=tolerance, min_coverage=min_coverage
            )
        ):
            return False
        # Sample inner polygon vertices and a few midpoints
        points: list[tuple[int, int]] = []
        for i in range(len(inner_arr)):
            points.append((int(inner_arr[i][0]), int(inner_arr[i][1])))
            nxt = inner_arr[(i + 1) % len(inner_arr)]
            mid = ((inner_arr[i][0] + nxt[0]) / 2, (inner_arr[i][1] + nxt[1]) / 2)
            points.append((int(mid[0]), int(mid[1])))
        inside = 0
        for pt in points:
            if cv2.pointPolygonTest(outer_arr, pt, False) >= -tolerance:
                inside += 1
        return inside / max(len(points), 1) >= min_coverage
    except Exception:
        return False


def build_token_graph(
    metrics: Sequence[Mapping[str, Any]],
    tolerance: int = 2,
    min_coverage: float = 0.9,
) -> list[dict[str, Any]]:
    """
    Build a simple token graph from component spacing metrics (bbox-based).

    Returns:
        List of nodes: {"id": str, "box": [x,y,w,h], "parent_id": str|None, "children": [str], "meta": {...}}
    """
    nodes: list[dict[str, Any]] = []
    for idx, metric in enumerate(metrics):
        if not isinstance(metric, Mapping):
            continue
        box = metric.get("box") or metric.get("bbox")
        polygon = metric.get("polygon")
        if polygon and not box:
            box = _polygon_bbox(polygon)
        if not box or len(box) != 4:
            continue
        node_id = str(metric.get("index", idx))
        nodes.append(
            {
                "id": node_id,
                "box": [int(box[0]), int(box[1]), int(box[2]), int(box[3])],
                "polygon": polygon,
                "meta": {
                    "neighbor_gap": metric.get("neighbor_gap"),
                    "padding": metric.get("padding"),
                    "type": metric.get("type"),
                    "corner_radius": metric.get("corner_radius"),
                    "border_width": metric.get("border_width"),
                },
                "parent_id": None,
                "children": [],
            }
        )

    # Containment relationships
    for child in nodes:
        cx, cy, cw, ch = child["box"]
        child_area = _box_area((cx, cy, cw, ch))
        candidates = []
        for parent in nodes:
            if parent is child:
                continue
            px, py, pw, ph = parent["box"]
            if _box_area((px, py, pw, ph)) <= child_area:
                continue
            poly_parent = parent.get("polygon")
            poly_child = child.get("polygon")
            if poly_parent and poly_child:
                contains = _poly_contains(poly_parent, poly_child, tolerance=tolerance)
            else:
                contains = _box_contains(
                    (px, py, pw, ph),
                    (cx, cy, cw, ch),
                    tolerance=tolerance,
                    min_coverage=min_coverage,
                )
            if contains:
                candidates.append(parent)
        if candidates:
            parent = min(candidates, key=lambda n: _box_area(tuple(n["box"])))
            child["parent_id"] = parent["id"]

    lookup = {n["id"]: n for n in nodes}
    for node in nodes:
        pid = node["parent_id"]
        if pid and pid in lookup:
            lookup[pid]["children"].append(node["id"])

    boxes = [tuple(n["box"]) for n in nodes]
    align = detect_alignment_lines(boxes, tolerance=max(tolerance, 3), min_support=2)
    gap_clusters = {
        "x": cluster_gaps(
            [b2[0] - (b1[0] + b1[2]) for b1 in boxes for b2 in boxes if b2[0] > b1[0]],
            tolerance=3,
        ),
        "y": cluster_gaps(
            [b2[1] - (b1[1] + b1[3]) for b1 in boxes for b2 in boxes if b2[1] > b1[1]],
            tolerance=3,
        ),
    }
    for node in nodes:
        node["meta"]["alignment"] = align
        node["meta"]["gap_clusters"] = gap_clusters

    return nodes


def validate_extraction(
    tokens: TypingSequence[Any],
    image: tuple[int, int] | Mapping[str, Any] | None,
    expected_types: Iterable[str] | None = None,
    min_tokens: int = 3,
    min_coverage: float = 0.2,
) -> dict[str, Any]:
    """
    Basic validation heuristics for extracted tokens.

    Args:
        tokens: Sequence of token-like objects/dicts. Should carry ``box``/``bbox`` (x, y, w, h).
        image: Tuple (width, height) or mapping with width/height keys.
        expected_types: Iterable of types we expect to see (e.g., ["text", "button"]).
        min_tokens: Minimum token count before we warn about low recall.
        min_coverage: Minimum fraction of image area that should be covered by token boxes.

    Returns:
        Dict with warnings and flags: {"warnings": [...], "coverage": float, "token_count": int}
    """
    warnings: list[str] = []

    if image is None:
        warnings.append("Image dimensions unavailable; coverage check skipped.")
        return {"warnings": warnings, "coverage": None, "token_count": len(tokens)}

    width: int | None = None
    height: int | None = None
    if isinstance(image, tuple) and len(image) == 2:
        width, height = int(image[0]), int(image[1])
    elif isinstance(image, Mapping):
        width = int(image.get("width") or image.get("w") or image.get("image_width") or 0)
        height = int(image.get("height") or image.get("h") or image.get("image_height") or 0)

    if not width or not height or width <= 0 or height <= 0:
        warnings.append("Invalid image dimensions; coverage check skipped.")
        return {"warnings": warnings, "coverage": None, "token_count": len(tokens)}

    # Count tokens
    token_count = len(tokens)
    if token_count == 0:
        warnings.append("No elements detected. The image may be unclear or the extractor failed.")
    elif token_count < min_tokens:
        warnings.append(f"Very few elements detected ({token_count}); results may be incomplete.")

    # Area coverage
    def _extract_box(item: Any) -> tuple[int, int, int, int] | None:
        candidate: Any | None = None
        if isinstance(item, Mapping):
            candidate = item.get("box") or item.get("bbox")
        elif hasattr(item, "box"):
            candidate = item.box
        elif hasattr(item, "bbox"):
            candidate = item.bbox
        if candidate is None:
            return None
        try:
            x, y, w, h = candidate  # type: ignore[misc]
            return (
                int(round(float(x))),
                int(round(float(y))),
                int(round(float(w))),
                int(round(float(h))),
            )
        except Exception:
            return None

    total_area = max(width * height, 1)
    covered_area = 0
    for tok in tokens:
        box = _extract_box(tok)
        if not box:
            continue
        x, y, w, h = box
        if w <= 0 or h <= 0:
            continue
        # clip to image bounds
        x2 = min(x + w, width)
        y2 = min(y + h, height)
        x1 = max(x, 0)
        y1 = max(y, 0)
        if x2 <= x1 or y2 <= y1:
            continue
        covered_area += (x2 - x1) * (y2 - y1)

    coverage = covered_area / total_area
    if coverage < min_coverage:
        warnings.append(
            f"Only {coverage:.0%} of the image is covered by detected elements; results may be incomplete."
        )

    # Expected type presence
    if expected_types:
        present = set()
        for tok in tokens:
            ttype = None
            if isinstance(tok, Mapping):
                ttype = tok.get("type") or tok.get("semantic_role")
            elif hasattr(tok, "type"):
                ttype = getattr(tok, "type", None)
            if ttype:
                present.add(str(ttype).lower())
        for expected in expected_types:
            if expected.lower() not in present:
                warnings.append(f"Expected element type '{expected}' not detected.")

    # Low confidence tokens (if confidence present)
    low_conf = [
        tok
        for tok in tokens
        if (
            isinstance(tok, Mapping)
            and isinstance(tok.get("padding_confidence") or tok.get("confidence"), (int, float))
            and float(tok.get("padding_confidence") or tok.get("confidence")) < 0.35
        )
        or (
            hasattr(tok, "confidence")
            and isinstance(tok.confidence, (int, float))
            and tok.confidence < 0.35
        )
    ]
    if low_conf:
        warnings.append(f"{len(low_conf)} elements are low confidence; verify their accuracy.")

    return {"warnings": warnings, "coverage": coverage, "token_count": token_count}


def detect_scale_system(spacing_values: list[int]) -> str:
    """
    Detect which scale system the spacing values follow.

    Analyzes the ratios between consecutive values to classify:
    - 4pt: 4, 8, 12, 16, 20... (linear with base 4)
    - 8pt: 8, 16, 24, 32... (linear with base 8)
    - golden: 1.618 ratio between steps
    - fibonacci: 1, 2, 3, 5, 8, 13...
    - linear: Equal increments
    - exponential: Multiplied increments
    - custom: Non-standard

    Args:
        spacing_values: List of spacing values

    Returns:
        Scale system identifier

    Example:
        >>> detect_scale_system([4, 8, 12, 16, 20, 24])
        '4pt'
        >>> detect_scale_system([8, 16, 24, 32, 40])
        '8pt'
    """
    if not spacing_values or len(spacing_values) < 2:
        return "custom"

    values = sorted(set(v for v in spacing_values if v > 0))

    if len(values) < 2:
        return "custom"

    base = detect_base_unit(values)

    # Check for 4pt or 8pt grid
    if base == 4 and all(v % 4 == 0 for v in values):
        return "4pt"
    elif base == 8 and all(v % 8 == 0 for v in values):
        return "8pt"

    # Check for fibonacci sequence
    fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    if all(v in fib or v in [f * 2 for f in fib] or v in [f * 4 for f in fib] for v in values):
        return "fibonacci"

    # Check for golden ratio (1.618)
    ratios = [values[i + 1] / values[i] for i in range(len(values) - 1) if values[i] > 0]
    if ratios and all(1.5 < r < 1.75 for r in ratios):
        return "golden"

    # Check for linear progression
    diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    if diffs and max(diffs) - min(diffs) <= 2:  # Allow small variance
        return "linear"

    # Check for exponential (constant multiplier)
    if ratios and max(ratios) - min(ratios) < 0.2:
        return "exponential"

    return "custom"


def detect_scale_position(value_px: int, spacing_values: list[int]) -> int:
    """
    Determine the position of a value in its scale (0-indexed).

    Args:
        value_px: Spacing value to position
        spacing_values: All values in the scale

    Returns:
        Position in scale (0 = smallest)

    Example:
        >>> detect_scale_position(16, [4, 8, 12, 16, 20, 24])
        3
        >>> detect_scale_position(8, [8, 16, 24, 32])
        0
    """
    sorted_values = sorted(set(spacing_values))

    if value_px in sorted_values:
        return sorted_values.index(value_px)

    # Find nearest position
    for i, v in enumerate(sorted_values):
        if v >= value_px:
            return i

    return len(sorted_values) - 1


def check_grid_compliance(value_px: int, grid_size: int = 8) -> tuple[bool, int]:
    """
    Check if a spacing value aligns to a grid system.

    Args:
        value_px: Spacing value to check
        grid_size: Grid unit size (default 8px)

    Returns:
        Tuple of (is_aligned, deviation_in_px)

    Example:
        >>> check_grid_compliance(16, grid_size=8)
        (True, 0)
        >>> check_grid_compliance(15, grid_size=8)
        (False, 1)
        >>> check_grid_compliance(18, grid_size=4)
        (False, 2)
    """
    remainder = value_px % grid_size

    if remainder == 0:
        return True, 0

    # Calculate deviation (distance to nearest grid point)
    deviation = min(remainder, grid_size - remainder)

    return False, deviation


def cluster_spacing_values(
    values: list[float], tolerance: float = 0.1, base_unit: int | None = None
) -> list[int]:
    """
    Snap/cluster spacing values to a base scale.

    Args:
        values: raw spacing values (px)
        tolerance: allowed relative error for rounding (e.g., 0.1 = 10%)
        base_unit: optional base unit; if None, derived from values

    Returns:
        Sorted unique spacing values (px) after clustering.
    """
    filtered = [v for v in values if v > 0]
    if not filtered:
        return []

    base = base_unit or detect_base_unit(filtered)
    snapped: list[int] = []
    for val in filtered:
        multiple = round(val / base)
        multiple = max(1, multiple)
        candidate = multiple * base
        # merge into existing snapped if within tolerance
        merged = False
        for _idx, existing in enumerate(snapped):
            if abs(existing - val) / max(val, 1e-6) <= tolerance:
                merged = True
                break
        if not merged:
            snapped.append(
                int(candidate if abs(candidate - val) / max(val, 1e-6) <= tolerance else round(val))
            )
    return sorted(set(snapped))


def detect_baseline_spacing_from_bboxes(
    bboxes: Iterable[tuple[int, int, int, int]],
    *,
    tolerance_px: int = 2,
    min_pairs: int = 3,
) -> tuple[int, float] | None:
    """
    Estimate vertical rhythm (baseline spacing) from bounding boxes.

    Args:
        bboxes: Iterable of (x, y, w, h) tuples.
        tolerance_px: Allowed px variance when clustering deltas.
        min_pairs: Minimum neighbor pairs required to report a baseline.

    Returns:
        (spacing_px, confidence) if detected, else None.
    """
    bottoms = sorted(b[1] + b[3] for b in bboxes if b[3] > 2)
    if len(bottoms) < 2:
        return None

    diffs = [bottoms[i + 1] - bottoms[i] for i in range(len(bottoms) - 1)]
    diffs = [int(round(d)) for d in diffs if d > tolerance_px]
    if len(diffs) < min_pairs:
        return None

    buckets: list[int] = []
    counts: Counter[int] = Counter()
    for diff in diffs:
        matched = None
        for existing in buckets:
            if abs(existing - diff) <= tolerance_px:
                matched = existing
                break
        if matched is None:
            buckets.append(diff)
            matched = diff
        counts[matched] += 1

    value, freq = counts.most_common(1)[0]
    coverage = freq / len(diffs)
    if freq < min_pairs and coverage < 0.3:
        return None
    return value, round(min(1.0, coverage), 4)


def detect_baseline_spacing_from_text_tokens(
    text_tokens: Iterable[Mapping[str, Any]],
    *,
    tolerance_px: int = 2,
    min_pairs: int = 2,
) -> tuple[int, float] | None:
    """
    Estimate baseline-to-baseline rhythm using text token bounding boxes.

    Text tokens are expected to provide ``bbox`` or ``box`` entries.
    """
    boxes: list[tuple[int, int, int, int]] = []
    for tok in text_tokens:
        box = tok.get("bbox") or tok.get("box")
        if not box or len(box) != 4:
            continue
        boxes.append(tuple(int(v) for v in box))
    if not boxes:
        return None
    result = detect_baseline_spacing_from_bboxes(boxes, tolerance_px=tolerance_px, min_pairs=min_pairs)
    if result is None:
        return None
    value, conf = result
    # Slightly boost confidence because text baselines are reliable
    return value, round(min(1.0, conf + 0.1), 4)


def build_text_spacing_candidates(
    text_tokens: Iterable[Mapping[str, Any]],
    *,
    tolerance_px: int = 2,
    min_pairs: int = 2,
) -> list[dict[str, Any]]:
    """Emit spacing candidates derived from text baselines."""
    detected = detect_baseline_spacing_from_text_tokens(
        text_tokens, tolerance_px=tolerance_px, min_pairs=min_pairs
    )
    if detected is None:
        return []
    spacing_px, confidence = detected
    candidates: list[dict[str, Any]] = []
    tokens = [t for t in text_tokens if (t.get("bbox") or t.get("box"))]
    tokens.sort(key=lambda t: (t.get("bbox") or t.get("box"))[1])  # type: ignore[index]
    for idx in range(len(tokens) - 1):
        a = tokens[idx]
        b = tokens[idx + 1]
        box_a = a.get("bbox") or a.get("box")
        box_b = b.get("bbox") or b.get("box")
        if not box_a or not box_b:
            continue
        candidates.append(
            {
                "node_a": str(a.get("id") or f"text-{idx}"),
                "node_b": str(b.get("id") or f"text-{idx+1}"),
                "axis": "y",
                "distance_px": spacing_px,
                "source": "text-baseline",
                "confidence": round(confidence, 4),
                "bbox_a": [int(v) for v in box_a],
                "bbox_b": [int(v) for v in box_b],
            }
        )
    return candidates


def spacing_tokens_from_values(values: list[float], unit: str = "px") -> dict[str, dict[str, Any]]:
    """
    Build spacing tokens from raw values.

    Returns:
        Dict of token id -> { "$type": "dimension", "$value": { "value": n, "unit": unit } }
    """
    clustered = cluster_spacing_values(values)
    tokens: dict[str, dict[str, Any]] = {}
    for idx, val in enumerate(clustered, start=1):
        tokens[f"spacing.{idx}"] = {"$type": "dimension", "$value": {"value": val, "unit": unit}}
    return tokens


def suggest_grid_aligned_value(value_px: int, grid_size: int = 8) -> int:
    """
    Suggest the nearest grid-aligned value.

    Args:
        value_px: Original spacing value
        grid_size: Grid unit size

    Returns:
        Nearest grid-aligned value

    Example:
        >>> suggest_grid_aligned_value(15, grid_size=8)
        16
        >>> suggest_grid_aligned_value(19, grid_size=8)
        16
        >>> suggest_grid_aligned_value(21, grid_size=8)
        24
    """
    remainder = value_px % grid_size

    if remainder == 0:
        return value_px

    # Round to nearest grid point
    if remainder < grid_size / 2:
        return value_px - remainder
    else:
        return value_px + (grid_size - remainder)


def suggest_responsive_scales(base_value_px: int, scale_type: str = "linear") -> dict[str, int]:
    """
    Generate suggested spacing values for responsive breakpoints.

    Creates a mapping of breakpoint to spacing value, scaling
    appropriately for different screen sizes.

    Args:
        base_value_px: Base value (typically for 'md' breakpoint)
        scale_type: How to scale ('linear', 'proportional', 'stepped')

    Returns:
        Dict mapping breakpoint to spacing value

    Example:
        >>> suggest_responsive_scales(16, scale_type='linear')
        {'xs': 8, 'sm': 12, 'md': 16, 'lg': 20, 'xl': 24, 'xxl': 28}
        >>> suggest_responsive_scales(24, scale_type='proportional')
        {'xs': 12, 'sm': 18, 'md': 24, 'lg': 30, 'xl': 36, 'xxl': 42}
    """
    if scale_type == "proportional":
        # Scale proportionally to viewport
        return {
            "xs": round(base_value_px * 0.5),
            "sm": round(base_value_px * 0.75),
            "md": base_value_px,
            "lg": round(base_value_px * 1.25),
            "xl": round(base_value_px * 1.5),
            "xxl": round(base_value_px * 1.75),
        }
    elif scale_type == "stepped":
        # Use discrete steps based on base unit
        base = detect_base_unit([base_value_px])
        return {
            "xs": max(base, base_value_px - base * 2),
            "sm": max(base, base_value_px - base),
            "md": base_value_px,
            "lg": base_value_px + base,
            "xl": base_value_px + base * 2,
            "xxl": base_value_px + base * 3,
        }
    else:  # linear
        # Linear scaling with fixed increment
        increment = round(base_value_px / 4)  # 25% steps
        return {
            "xs": max(4, base_value_px - increment * 2),
            "sm": max(4, base_value_px - increment),
            "md": base_value_px,
            "lg": base_value_px + increment,
            "xl": base_value_px + increment * 2,
            "xxl": base_value_px + increment * 3,
        }


def generate_scale_from_base(
    base_unit: int, num_steps: int = 10, scale_type: str = "linear"
) -> list[int]:
    """
    Generate a complete spacing scale from a base unit.

    Args:
        base_unit: Base unit in pixels
        num_steps: Number of scale steps to generate
        scale_type: Scale system ('4pt', '8pt', 'fibonacci', 'golden')

    Returns:
        List of spacing values

    Example:
        >>> generate_scale_from_base(4, num_steps=6)
        [4, 8, 12, 16, 20, 24]
        >>> generate_scale_from_base(8, num_steps=5, scale_type='8pt')
        [8, 16, 24, 32, 40]
    """
    if scale_type in ("4pt", "8pt", "linear"):
        return [base_unit * (i + 1) for i in range(num_steps)]

    elif scale_type == "fibonacci":
        fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        return [base_unit * f for f in fib[:num_steps]]

    elif scale_type == "golden":
        scale = [base_unit]
        for _ in range(num_steps - 1):
            scale.append(round(scale[-1] * 1.618))
        return scale

    elif scale_type == "exponential":
        return [round(base_unit * (1.5**i)) for i in range(num_steps)]

    return [base_unit * (i + 1) for i in range(num_steps)]


def compute_all_spacing_properties(value_px: int, all_values: list[int] | None = None) -> dict:
    """
    Compute all spacing properties at once.

    Similar to color_utils.compute_all_properties, this function
    calculates all derived properties for a spacing value.

    Args:
        value_px: Spacing value in pixels
        all_values: All spacing values for context (scale detection)

    Returns:
        Dictionary with all computed properties

    Example:
        >>> props = compute_all_spacing_properties(16, [4, 8, 12, 16, 20, 24])
        >>> props['value_rem']
        1.0
        >>> props['scale_system']
        '4pt'
        >>> props['grid_aligned']
        True
    """
    all_values = all_values or [value_px]

    # Check grid compliance for common grids
    grid_8_aligned, grid_8_deviation = check_grid_compliance(value_px, 8)
    grid_4_aligned, grid_4_deviation = check_grid_compliance(value_px, 4)

    # Prefer 8pt grid if aligned, else 4pt
    if grid_8_aligned:
        grid_aligned = True
        grid_deviation = 0
        detected_grid = 8
    elif grid_4_aligned:
        grid_aligned = True
        grid_deviation = 0
        detected_grid = 4
    else:
        grid_aligned = False
        grid_deviation = min(grid_4_deviation, grid_8_deviation)
        detected_grid = 4 if grid_4_deviation <= grid_8_deviation else 8

    properties = {
        # Unit conversions
        "value_rem": px_to_rem(value_px),
        "value_em": px_to_em(value_px),
        # Scale analysis
        "base_unit": detect_base_unit(all_values),
        "scale_system": detect_scale_system(all_values),
        "scale_position": detect_scale_position(value_px, all_values),
        # Grid compliance
        "grid_aligned": grid_aligned,
        "grid_deviation_px": grid_deviation,
        "detected_grid": detected_grid,
        "suggested_value": suggest_grid_aligned_value(value_px, detected_grid),
        # Responsive suggestions
        "responsive_scales": suggest_responsive_scales(value_px),
        # Tailwind mapping
        "tailwind_value": value_px / 4 if value_px % 4 == 0 else None,
    }

    return properties


def compute_all_spacing_properties_with_metadata(
    value_px: int, all_values: list[int] | None = None
) -> tuple[dict, dict]:
    """
    Compute all spacing properties and track their extraction sources.

    Follows the pattern of color_utils.compute_all_properties_with_metadata.

    Args:
        value_px: Spacing value in pixels
        all_values: All spacing values for context

    Returns:
        Tuple of (properties dict, metadata dict mapping field names to tool sources)
    """
    properties = compute_all_spacing_properties(value_px, all_values)

    # Track which tool extracted each property
    metadata = {
        "value_rem": "spacing_utils.px_to_rem",
        "value_em": "spacing_utils.px_to_em",
        "base_unit": "spacing_utils.detect_base_unit",
        "scale_system": "spacing_utils.detect_scale_system",
        "scale_position": "spacing_utils.detect_scale_position",
        "grid_aligned": "spacing_utils.check_grid_compliance",
        "grid_deviation_px": "spacing_utils.check_grid_compliance",
        "detected_grid": "spacing_utils.check_grid_compliance",
        "suggested_value": "spacing_utils.suggest_grid_aligned_value",
        "responsive_scales": "spacing_utils.suggest_responsive_scales",
        "tailwind_value": "spacing_utils.compute_all_spacing_properties",
    }

    return properties, metadata


def calculate_spacing_similarity(
    value1: int, value2: int, threshold_percentage: float = 10.0
) -> tuple[bool, float]:
    """
    Check if two spacing values are similar within a percentage threshold.

    Unlike colors which use Delta-E, spacing uses percentage-based comparison.

    Args:
        value1: First spacing value
        value2: Second spacing value
        threshold_percentage: Percentage threshold for similarity

    Returns:
        Tuple of (is_similar, percentage_difference)

    Example:
        >>> calculate_spacing_similarity(15, 16)
        (True, 6.25)
        >>> calculate_spacing_similarity(10, 20)
        (False, 100.0)
    """
    if value1 == value2:
        return True, 0.0

    if value1 == 0 or value2 == 0:
        return False, 100.0

    # Calculate percentage difference relative to smaller value
    diff = abs(value1 - value2)
    base = min(value1, value2)
    percentage = (diff / base) * 100

    return percentage <= threshold_percentage, round(percentage, 2)


def merge_similar_spacings(spacings: list[int], threshold_percentage: float = 15.0) -> list[int]:
    """
    Merge similar spacing values within a threshold.

    Similar to color_utils.merge_similar_colors, but for spacing values.

    Args:
        spacings: List of spacing values
        threshold_percentage: Percentage threshold for merging

    Returns:
        List of representative spacing values after merging

    Example:
        >>> merge_similar_spacings([15, 16, 17, 32])
        [16, 32]
    """
    if not spacings:
        return []

    sorted_spacings = sorted(set(spacings))
    merged = []
    current_group = [sorted_spacings[0]]

    for value in sorted_spacings[1:]:
        is_similar, _ = calculate_spacing_similarity(current_group[0], value, threshold_percentage)

        if is_similar:
            current_group.append(value)
        else:
            # Save average of current group
            merged.append(round(sum(current_group) / len(current_group)))
            current_group = [value]

    # Don't forget last group
    if current_group:
        merged.append(round(sum(current_group) / len(current_group)))

    return merged
