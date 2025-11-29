"""
Spacing Utility Functions

Utility functions for spacing calculations, scale detection, and grid compliance.
Follows the pattern of color_utils.py.
"""

from collections import Counter
from collections.abc import Sequence
from functools import reduce
from typing import Any


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


def infer_base_spacing(spacing_values: list[int]) -> tuple[int, float]:
    """
    Infer the base spacing unit and a confidence score from a set of gaps using
    frequency/mode analysis.

    Args:
        spacing_values: List of gap measurements (pixels)

    Returns:
        (base_unit, confidence) where confidence is the fraction of values
        that are multiples of the inferred base (0.0–1.0).
    """
    values = [int(v) for v in spacing_values if v > 0]
    if not values:
        return 8, 0.0

    counts = Counter(values)
    mode_value, mode_freq = counts.most_common(1)[0]

    # Candidate bases: mode, min, detected gcd
    candidates = {mode_value, min(values), detect_base_unit(values)}
    best_base = min(candidates)  # prefer smaller consistent bases

    def aligns(v: int, base: int) -> bool:
        return base > 0 and (v % base == 0 or abs(v - round(v / base) * base) <= 1)

    total = sum(counts.values()) or 1
    align_total = sum(freq for val, freq in counts.items() if aligns(val, best_base))
    confidence = round(align_total / total, 4)
    return best_base or 8, min(confidence, 1.0)


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
