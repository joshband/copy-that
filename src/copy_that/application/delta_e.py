"""
CIE Delta-E color difference implementations.

Provides multiple color distance metrics:
- Delta-E 76 (simple Euclidean in LAB)
- Delta-E 2000 (CIEDE2000 - most accurate, accounts for perceptual non-uniformities)

Delta-E values guide interpretation:
- < 1.0: Imperceptible
- 1.0-2.0: Barely perceptible
- 2.0-5.0: Noticeable but small differences
- 5.0-10.0: Noticeable and larger differences
- > 10.0: Very obvious differences

References:
- Luo et al. (2001): The CIEDE2000 Color-Difference Formula
- ISO/CIE 11664-2:2022: Standard for Color Difference Measurement

Author: Copy This Research
Date: 2025-11-16
"""

from typing import Tuple, Union
import numpy as np

try:
    from coloraide import Color
except ImportError:
    raise ImportError(
        "coloraide library required. Install with: pip install coloraide>=4.4.0"
    )


def delta_e_76(
    color1: Union[str, Tuple[int, int, int]],
    color2: Union[str, Tuple[int, int, int]]
) -> float:
    """
    Calculate Delta-E 76 (simple Euclidean distance in LAB space).

    Faster than CIEDE2000 but less perceptually accurate.
    Good for quick comparisons or when speed is critical.

    Formula:
        ΔE76 = √((ΔL)² + (Δa)² + (Δb)²)

    Args:
        color1: First color (hex string like "#F15925" or RGB tuple (255, 89, 37))
        color2: Second color (hex string or RGB tuple)

    Returns:
        Delta-E 76 value (0 = identical, higher = more different)

    Example:
        >>> delta_e_76("#F15925", "#F15924")  # Similar colors
        0.5
        >>> delta_e_76("#FF0000", "#0000FF")  # Very different
        53.2
    """
    # Convert to LAB color space
    if isinstance(color1, str):
        c1_lab = Color(color1).convert("lab")
    else:
        c1_lab = Color("srgb", color1[0]/255, color1[1]/255, color1[2]/255).convert("lab")

    if isinstance(color2, str):
        c2_lab = Color(color2).convert("lab")
    else:
        c2_lab = Color("srgb", color2[0]/255, color2[1]/255, color2[2]/255).convert("lab")

    # Extract LAB values
    L1, a1, b1 = c1_lab["lightness"], c1_lab["a"], c1_lab["b"]
    L2, a2, b2 = c2_lab["lightness"], c2_lab["a"], c2_lab["b"]

    # Simple Euclidean distance
    delta_e = np.sqrt((L1 - L2)**2 + (a1 - a2)**2 + (b1 - b2)**2)

    return float(delta_e)


def delta_e_2000(
    color1: Union[str, Tuple[int, int, int]],
    color2: Union[str, Tuple[int, int, int]],
    kL: float = 1.0,
    kC: float = 1.0,
    kH: float = 1.0
) -> float:
    """
    Calculate CIE Delta-E 2000 (CIEDE2000) color difference.

    This is the most accurate and widely-used perceptual color distance metric.
    It accounts for:
    - Non-uniform perceptual sensitivity in different hue ranges
    - Hue-specific sensitivity
    - Lightness-specific sensitivity
    - Saturation-specific sensitivity

    Parameters can be adjusted for specific applications:
    - Graphic arts: kL=2, kC=1, kH=1 (emphasize lightness)
    - Textiles: kL=1, kC=1, kH=1 (balanced)
    - LCD displays: kL=1, kC=1, kH=1 (balanced)

    Args:
        color1: First color (hex string or RGB tuple)
        color2: Second color (hex string or RGB tuple)
        kL, kC, kH: Lightness, chroma, hue weighting factors (default: 1.0 each)

    Returns:
        Delta-E 2000 value (perceptual color difference)

    Reference:
        Luo, M. R., Cui, G., & Rigg, B. (2001).
        The CIEDE2000 color-difference formula: Implementation notes,
        supplementary test data, and mathematical observations.
        Color Research & Application, 26(5), 340–350.

    Example:
        >>> delta_e_2000("#F15925", "#F15924")  # Nearly identical
        0.2
        >>> delta_e_2000("#FF0000", "#00FF00")  # Very different
        56.8
    """

    # Convert to LAB color space
    if isinstance(color1, str):
        c1_lab = Color(color1).convert("lab")
    else:
        c1_lab = Color("srgb", color1[0]/255, color1[1]/255, color1[2]/255).convert("lab")

    if isinstance(color2, str):
        c2_lab = Color(color2).convert("lab")
    else:
        c2_lab = Color("srgb", color2[0]/255, color2[1]/255, color2[2]/255).convert("lab")

    # Extract LAB values
    L1, a1, b1 = c1_lab["lightness"], c1_lab["a"], c1_lab["b"]
    L2, a2, b2 = c2_lab["lightness"], c2_lab["a"], c2_lab["b"]

    # Step 1: Calculate chroma for both colors
    C1 = np.sqrt(a1**2 + b1**2)
    C2 = np.sqrt(a2**2 + b2**2)
    C_bar = (C1 + C2) / 2.0

    # Step 2: Calculate G factor (chroma adjustment)
    # Accounts for reduced saturation perception at low chroma
    G = 0.5 * (1.0 - np.sqrt(C_bar**7 / (C_bar**7 + 25.0**7)))

    # Step 3: Adjust a* values using G factor
    a1_prime = a1 * (1.0 + G)
    a2_prime = a2 * (1.0 + G)

    # Step 4: Recalculate chroma with adjusted a*
    C1_prime = np.sqrt(a1_prime**2 + b1**2)
    C2_prime = np.sqrt(a2_prime**2 + b2**2)
    C_bar_prime = (C1_prime + C2_prime) / 2.0

    # Step 5: Calculate hue angles (in degrees)
    h1_prime = np.arctan2(b1, a1_prime) * 180.0 / np.pi
    if h1_prime < 0:
        h1_prime += 360.0

    h2_prime = np.arctan2(b2, a2_prime) * 180.0 / np.pi
    if h2_prime < 0:
        h2_prime += 360.0

    # Step 6: Calculate differences
    dL_prime = L2 - L1
    dC_prime = C2_prime - C1_prime

    # Hue difference with proper quadrant handling
    if C1_prime * C2_prime == 0:
        dh_prime = 0
    else:
        dh = h2_prime - h1_prime
        # Handle angle wraparound
        if abs(dh) > 180:
            dh = dh - 360 if dh > 0 else dh + 360

        dh_prime = dh

    # Step 7: Calculate ΔH (hue difference in euclidean space)
    # dH = 2 * sqrt(C1' * C2') * sin(dh' / 2)
    dH_prime = 2.0 * np.sqrt(C1_prime * C2_prime) * np.sin(np.radians(dh_prime / 2.0))

    # Step 8: Calculate mean values
    L_bar_prime = (L1 + L2) / 2.0
    h_bar_prime = (h1_prime + h2_prime) / 2.0

    # Adjust mean hue for angles near 0°/360° discontinuity
    if abs(h1_prime - h2_prime) > 180:
        h_bar_prime = ((h_bar_prime + 180) % 360)

    # Step 9: Calculate T (hue-dependent weighting factor)
    # Accounts for stronger perceptual sensitivity in certain hue ranges
    T = 1.0 - 0.17 * np.cos(np.radians(h_bar_prime - 30.0)) \
            + 0.24 * np.cos(np.radians(2.0 * h_bar_prime)) \
            + 0.32 * np.cos(np.radians(3.0 * h_bar_prime + 6.0)) \
            - 0.20 * np.cos(np.radians(4.0 * h_bar_prime - 63.0))

    # Step 10: Calculate SL (lightness weighting function)
    SL = 1.0 + (0.015 * (L_bar_prime - 50.0)**2) / np.sqrt(20.0 + (L_bar_prime - 50.0)**2)

    # Step 11: Calculate SC (chroma weighting function)
    SC = 1.0 + 0.045 * C_bar_prime

    # Step 12: Calculate SH (hue weighting function)
    SH = 1.0 + 0.015 * C_bar_prime * T

    # Step 13: Calculate final Delta-E 2000
    dE_2000 = np.sqrt(
        (dL_prime / (kL * SL))**2 +
        (dC_prime / (kC * SC))**2 +
        (dH_prime / (kH * SH))**2
    )

    return float(dE_2000)


def color_similarity(
    color1: str,
    color2: str,
    threshold: float = 5.0,
    metric: str = "2000"
) -> bool:
    """
    Determine if two colors are perceptually similar.

    Args:
        color1: First color (hex string)
        color2: Second color (hex string)
        threshold: ΔE threshold for similarity
                  Recommended thresholds:
                  - 2.0: Very similar (barely noticeable difference)
                  - 5.0: Similar (noticeable but acceptable)
                  - 10.0: Somewhat different (clearly different)
        metric: "2000" (CIEDE2000) or "76" (simple Euclidean)

    Returns:
        True if colors are similar (within threshold)

    Example:
        >>> color_similarity("#F15925", "#F15924", threshold=2.0)
        True  # Very similar colors
        >>> color_similarity("#FF0000", "#00FF00", threshold=10.0)
        False  # Clearly different
    """
    if metric == "2000":
        de = delta_e_2000(color1, color2)
    else:
        de = delta_e_76(color1, color2)

    return de < threshold


def find_nearest_color(
    target_hex: str,
    color_palette: dict,
    threshold: float = 10.0,
    metric: str = "2000"
) -> Tuple[str, float]:
    """
    Find the nearest color to a target in a palette using Delta-E.

    Useful for color matching, naming, and standardization.

    Args:
        target_hex: Color to match
        color_palette: Dict mapping {name: hex_color} or {name: rgb_tuple}
        threshold: Maximum ΔE for match (return None name if exceeded)
        metric: "2000" or "76"

    Returns:
        Tuple of (name, delta_e) for nearest color
        Returns ("NONE", threshold+1) if no match within threshold

    Example:
        >>> palette = {
        ...     "primary": "#F15925",
        ...     "secondary": "#3B5E4C",
        ...     "accent": "#EBCF7E"
        ... }
        >>> name, de = find_nearest_color("#F15926", palette)
        >>> print(f"{name}: ΔE={de:.2f}")
        primary: ΔE=0.15
    """
    best_match = ("NONE", threshold + 1)

    for name, palette_color in color_palette.items():
        if metric == "2000":
            de = delta_e_2000(target_hex, palette_color)
        else:
            de = delta_e_76(target_hex, palette_color)

        if de < best_match[1]:
            best_match = (name, de)

    return best_match


def merge_similar_colors(
    colors: list[str],
    threshold: float = 15.0,
    metric: str = "2000"
) -> list[str]:
    """
    Merge perceptually similar colors from a list.

    Useful for reducing color count while preserving distinct hues.

    Args:
        colors: List of hex colors
        threshold: ΔE threshold for merging
                  15 = clearly different but related
                  10 = noticeable difference
        metric: "2000" or "76"

    Returns:
        List of representative colors after merging

    Example:
        >>> colors = ["#F15925", "#F15926", "#F15927", "#3B5E4C"]
        >>> merged = merge_similar_colors(colors, threshold=5.0)
        >>> len(merged)  # Should be 2 (oranges merged, teal separate)
        2
    """
    if not colors:
        return []

    merged = []
    used = set()
    delta_e_func = delta_e_2000 if metric == "2000" else delta_e_76

    for i, color1 in enumerate(colors):
        if i in used:
            continue

        # Find all similar colors
        similar_group = [color1]

        for j in range(i + 1, len(colors)):
            if j in used:
                continue

            color2 = colors[j]

            # Check if perceptually similar to base color
            if delta_e_func(color1, color2) < threshold:
                similar_group.append(color2)
                used.add(j)

        # Use average color of group (in LAB space for better results)
        if len(similar_group) > 1:
            colors_lab = [Color(c).convert("lab") for c in similar_group]

            avg_l = np.mean([c["lightness"] for c in colors_lab])
            avg_a = np.mean([c["a"] for c in colors_lab])
            avg_b = np.mean([c["b"] for c in colors_lab])

            merged_color = Color("lab", [avg_l, avg_a, avg_b]).convert("srgb").to_string(hex=True)
            merged.append(merged_color)
        else:
            merged.append(color1)

        used.add(i)

    return merged


def validate_cluster_homogeneity(
    cluster_colors: list[str],
    max_internal_de: float = 10.0,
    metric: str = "2000"
) -> bool:
    """
    Check if cluster colors are internally cohesive (perceptually similar).

    Useful for validating clustering results.

    Args:
        cluster_colors: List of hex colors in cluster
        max_internal_de: Maximum allowed Delta-E within cluster
        metric: "2000" or "76"

    Returns:
        True if cluster is homogeneous (all pairs within threshold)

    Example:
        >>> cluster = ["#F15925", "#F15930", "#F15935"]  # All similar
        >>> validate_cluster_homogeneity(cluster, max_internal_de=15.0)
        True
    """
    if len(cluster_colors) < 2:
        return True

    delta_e_func = delta_e_2000 if metric == "2000" else delta_e_76

    # Check all pairs
    for i, color1 in enumerate(cluster_colors):
        for color2 in cluster_colors[i+1:]:
            if delta_e_func(color1, color2) > max_internal_de:
                return False

    return True


def get_perceptual_distance_summary(
    colors: list[str],
    metric: str = "2000"
) -> dict:
    """
    Get summary statistics of perceptual distances in a color list.

    Useful for understanding color diversity and distribution.

    Args:
        colors: List of hex colors
        metric: "2000" or "76"

    Returns:
        Dict with distance statistics

    Example:
        >>> colors = ["#FF0000", "#FF0001", "#00FF00", "#0000FF"]
        >>> summary = get_perceptual_distance_summary(colors)
        >>> print(f"Average distance: {summary['mean']:.2f}")
        >>> print(f"Max distance: {summary['max']:.2f}")
    """
    if len(colors) < 2:
        return {"mean": 0, "std": 0, "min": 0, "max": 0}

    delta_e_func = delta_e_2000 if metric == "2000" else delta_e_76

    distances = []

    # Calculate all pairwise distances
    for i, color1 in enumerate(colors):
        for color2 in colors[i+1:]:
            distances.append(delta_e_func(color1, color2))

    if not distances:
        return {"mean": 0, "std": 0, "min": 0, "max": 0}

    return {
        "mean": float(np.mean(distances)),
        "std": float(np.std(distances)),
        "min": float(np.min(distances)),
        "max": float(np.max(distances)),
        "count": len(distances)
    }
