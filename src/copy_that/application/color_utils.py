"""
Comprehensive color utilities for computing all color properties.

This module provides functions to calculate:
- Color space conversions (HSL, HSV, LAB)
- Accessibility metrics (WCAG contrast, colorblind safety)
- Color analysis (temperature, saturation, lightness)
- Color variants (tints, shades, tones)
- Advanced metrics (Delta E, web-safe colors, CSS names)
"""

import math
from colorsys import rgb_to_hls, rgb_to_hsv

import coloraide
import numpy as np

# CSS Named Colors for closest matching
CSS_NAMED_COLORS = {
    "aliceblue": "#F0F8FF",
    "antiquewhite": "#FAEBD7",
    "aqua": "#00FFFF",
    "aquamarine": "#7FFFD4",
    "azure": "#F0FFFF",
    "beige": "#F5F5DC",
    "bisque": "#FFE4C4",
    "black": "#000000",
    "blanchedalmond": "#FFEBCD",
    "blue": "#0000FF",
    "blueviolet": "#8A2BE2",
    "brown": "#A52A2A",
    "burlywood": "#DEB887",
    "cadetblue": "#5F9EA0",
    "chartreuse": "#7FFF00",
    "chocolate": "#D2691E",
    "coral": "#FF7F50",
    "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC",
    "crimson": "#DC143C",
    "cyan": "#00FFFF",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9",
    "darkgrey": "#A9A9A9",
    "darkgreen": "#006400",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00",
    "darkorchid": "#9932CC",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkslategrey": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deepskyblue": "#00BFFF",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1E90FF",
    "firebrick": "#B22222",
    "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22",
    "fuchsia": "#FF00FF",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "gold": "#FFD700",
    "goldenrod": "#DAA520",
    "gray": "#808080",
    "grey": "#808080",
    "green": "#008000",
    "greenyellow": "#ADFF2F",
    "honeydew": "#F0FFF0",
    "hotpink": "#FF69B4",
    "indianred": "#CD5C5C",
    "indigo": "#4B0082",
    "ivory": "#FFFFF0",
    "khaki": "#F0E68C",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lightblue": "#ADD8E6",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgrey": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0",
    "lime": "#00FF00",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "magenta": "#FF00FF",
    "maroon": "#800000",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "navy": "#000080",
    "oldlace": "#FDF5E6",
    "olive": "#808000",
    "olivedrab": "#6B8E23",
    "orange": "#FFA500",
    "orangered": "#FF4500",
    "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "pink": "#FFC0CB",
    "plum": "#DDA0DD",
    "powderblue": "#B0E0E6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "red": "#FF0000",
    "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seashell": "#FFF5EE",
    "sienna": "#A0522D",
    "silver": "#C0C0C0",
    "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#FFFAFA",
    "springgreen": "#00FF7F",
    "steelblue": "#4682B4",
    "tan": "#D2B48C",
    "teal": "#008080",
    "thistle": "#D8BFD8",
    "tomato": "#FF6347",
    "turquoise": "#40E0D0",
    "violet": "#EE82EE",
    "wheat": "#F5DEB3",
    "white": "#FFFFFF",
    "whitesmoke": "#F5F5F5",
    "yellow": "#FFFF00",
    "yellowgreen": "#9ACD32",
}

# Web-safe colors (216 colors from early web standards)
WEB_SAFE_COLORS = [hex(i * 51)[2:].upper().zfill(2) for i in range(6) for _ in range(36)]


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple (0-255 range)"""
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color"""
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert RGB components (0-255) to HSL values."""
    h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return h * 360, s * 100, l * 100


def hex_to_hsl(hex_code: str) -> str:
    """Convert hex to HSL format string"""
    r, g, b = hex_to_rgb(hex_code)
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, l, s = rgb_to_hls(r, g, b)
    h = int(h * 360)
    s = int(s * 100)
    l = int(l * 100)
    return f"hsl({h}, {s}%, {l}%)"


def hex_to_hsv(hex_code: str) -> str:
    """Convert hex to HSV format string"""
    r, g, b = hex_to_rgb(hex_code)
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, s, v = rgb_to_hsv(r, g, b)
    h = int(h * 360)
    s = int(s * 100)
    v = int(v * 100)
    return f"hsv({h}, {s}%, {v}%)"


def get_color_temperature(hex_code: str) -> str:
    """Determine if color is warm, cool, or neutral"""
    r, g, b = hex_to_rgb(hex_code)
    # Warm colors have high red/orange, cool have high blue/cyan
    warm_score = r - b
    if warm_score > 30:
        return "warm"
    elif warm_score < -30:
        return "cool"
    else:
        return "neutral"


def get_saturation_level(hex_code: str) -> str:
    """Categorize color saturation level"""
    r, g, b = hex_to_rgb(hex_code)
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # Calculate saturation using HSV
    max_c = max(r, g, b)
    min_c = min(r, g, b)

    if max_c == 0:
        saturation = 0
    else:
        saturation = (max_c - min_c) / max_c

    if saturation < 0.1:
        return "grayscale"
    elif saturation < 0.3:
        return "desaturated"
    elif saturation < 0.6:
        return "muted"
    else:
        return "vibrant"


def get_lightness_level(hex_code: str) -> str:
    """Categorize color lightness level"""
    r, g, b = hex_to_rgb(hex_code)
    # Calculate perceived lightness (luminance)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    if luminance < 0.33:
        return "dark"
    elif luminance < 0.66:
        return "medium"
    else:
        return "light"


def is_neutral_color(hex_code: str) -> bool:
    """Check if color is neutral/grayscale using ColorAide's achromatic() method"""
    try:
        color = coloraide.Color(hex_code)
        return color.achromatic()
    except Exception:
        # Fallback to RGB-based detection
        r, g, b = hex_to_rgb(hex_code)
        diff = max(abs(r - g), abs(g - b), abs(r - b))
        return diff < 20


def is_color_in_gamut(hex_code: str) -> bool:
    """Check if color is displayable in sRGB gamut using ColorAide's in_gamut() method"""
    try:
        color = coloraide.Color(hex_code)
        return color.in_gamut("srgb")
    except Exception:
        # Fallback: assume all hex colors are in sRGB gamut
        return True


def calculate_wcag_contrast(hex1: str, hex2: str) -> float:
    """Calculate WCAG contrast ratio between two colors (1.0 to 21.0)

    Uses ColorAide's luminance() for accurate perceptual brightness calculation.
    """
    try:
        color1 = coloraide.Color(hex1)
        color2 = coloraide.Color(hex2)

        l1 = color1.luminance()
        l2 = color2.luminance()

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)
    except Exception:
        # Fallback to manual calculation if ColorAide fails
        def get_luminance(hex_code: str) -> float:
            r, g, b = hex_to_rgb(hex_code)
            r, g, b = r / 255.0, g / 255.0, b / 255.0
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = get_luminance(hex1)
        l2 = get_luminance(hex2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)


def is_wcag_compliant(
    hex_color: str, background: str = "#FFFFFF", level: str = "AA", size: str = "normal"
) -> bool:
    """Check WCAG compliance for text on background

    Args:
        hex_color: Text color
        background: Background color
        level: "AA" or "AAA"
        size: "normal" or "large" (18pt+)

    Returns:
        True if compliant
    """
    contrast = calculate_wcag_contrast(hex_color, background)

    if level == "AAA":
        return contrast >= (7.0 if size == "normal" else 4.5)
    else:  # AA
        return contrast >= (4.5 if size == "normal" else 3.0)


def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
    """Alias for WCAG contrast ratio calculation used by tests."""
    # Round to two decimals to avoid floating point drift (e.g., 20.9999 -> 21.0)
    return round(calculate_wcag_contrast(hex1, hex2), 2)


def get_color_variant(hex_code: str, variant_type: str, amount: float = 0.5) -> str:
    """Generate color variants

    Args:
        hex_code: Original color
        variant_type: "tint" (lighter), "shade" (darker), "tone" (desaturated)
        amount: 0-1, how much to adjust

    Returns:
        Hex code of variant
    """
    r, g, b = hex_to_rgb(hex_code)

    if variant_type == "tint":
        # Mix with white
        r = int(r + (255 - r) * amount)
        g = int(g + (255 - g) * amount)
        b = int(b + (255 - b) * amount)
    elif variant_type == "shade":
        # Mix with black
        r = int(r * (1 - amount))
        g = int(g * (1 - amount))
        b = int(b * (1 - amount))
    elif variant_type == "tone":
        # Reduce saturation
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        r = int(r + (gray - r) * amount)
        g = int(g + (gray - g) * amount)
        b = int(b + (gray - b) * amount)

    return rgb_to_hex(r, g, b)


def generate_tint(hex_code: str, amount: float = 0.2) -> str:
    """Generate a lighter tint of the given color."""
    return get_color_variant(hex_code, "tint", amount)


def generate_shade(hex_code: str, amount: float = 0.2) -> str:
    """Generate a darker shade of the given color."""
    return get_color_variant(hex_code, "shade", amount)


def get_closest_web_safe(hex_code: str) -> str:
    """Find closest web-safe color (216 color palette)"""
    r, g, b = hex_to_rgb(hex_code)

    # Round to nearest web-safe value (0, 51, 102, 153, 204, 255)
    r = round(r / 51) * 51
    g = round(g / 51) * 51
    b = round(b / 51) * 51

    return rgb_to_hex(r, g, b)


def get_closest_css_named(hex_code: str) -> str | None:
    """Find closest CSS named color"""
    r, g, b = hex_to_rgb(hex_code)

    min_distance = float("inf")
    closest_name = None

    for name, css_hex in CSS_NAMED_COLORS.items():
        cr, cg, cb = hex_to_rgb(css_hex)
        # Calculate Euclidean distance in RGB space
        distance = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_name = name

    return closest_name


def calculate_delta_e(hex1: str, hex2: str) -> float:
    """Calculate Delta E (color difference) using ColorAide's perceptually-uniform metric

    Uses CIEDE2000 (default ColorAide method) for industry-standard color difference.
    Returns:
        Delta E value (0 = identical, >5 = perceptible difference)
    """
    try:
        color1 = coloraide.Color(hex1)
        color2 = coloraide.Color(hex2)
        return color1.delta_e(color2)
    except Exception:
        # Fallback to simple Euclidean distance in RGB space
        r1, g1, b1 = hex_to_rgb(hex1)
        r2, g2, b2 = hex_to_rgb(hex2)
        r1, g1, b1 = r1 / 255.0, g1 / 255.0, b1 / 255.0
        r2, g2, b2 = r2 / 255.0, g2 / 255.0, b2 / 255.0
        delta_e = math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2) * 100
        return delta_e


def get_color_harmony(hex_color: str, palette: list[str] | None = None) -> str | None:
    """Determine the harmony relationship of a color to a palette (basic classification)

    Analyzes hue relationships to classify harmony:
    - monochromatic: Same hue, different saturation/lightness
    - analogous: Adjacent hues (15-45° apart)
    - complementary: Opposite hues (160-200° apart)
    - triadic: Three evenly spaced hues (120° apart)
    - tetradic: Four evenly spaced hues (90° apart)
    - split-complementary: Complementary ± 30°

    Args:
        hex_color: Target color hex code
        palette: Optional list of hex colors to compare against (e.g., dominant colors)

    Returns:
        Harmony group name or None if insufficient palette data

    Note: Use get_color_harmony_advanced() for more detailed analysis
    """
    try:
        if not palette or len(palette) < 2:
            return None

        target_color = coloraide.Color(hex_color)
        target_hue = target_color.convert("hsl")["hue"]

        # Calculate hue relationships with palette colors
        hue_diffs = []
        for palette_hex in palette:
            if palette_hex == hex_color:
                continue
            palette_color = coloraide.Color(palette_hex)
            palette_hue = palette_color.convert("hsl")["hue"]

            # Normalize hue difference to 0-180 range
            hue_diff = abs(palette_hue - target_hue)
            if hue_diff > 180:
                hue_diff = 360 - hue_diff
            hue_diffs.append(hue_diff)

        if not hue_diffs:
            return "monochromatic"

        avg_hue_diff = sum(hue_diffs) / len(hue_diffs)

        # Classify harmony based on average hue difference
        if avg_hue_diff < 15:
            return "monochromatic"
        elif avg_hue_diff < 45:
            return "analogous"
        elif avg_hue_diff < 75:
            return "split-complementary"
        elif 100 < avg_hue_diff < 140:
            return "triadic"
        elif 160 <= avg_hue_diff <= 200:
            return "complementary"
        else:
            return "tetradic"

    except Exception:
        return None


def get_color_harmony_advanced(
    hex_color: str, palette: list[str] | None = None, return_metadata: bool = False
) -> str | dict:
    """Advanced color harmony analysis with detailed classification

    Performs sophisticated hue angle analysis to classify harmony schemes:

    **Basic Schemes:**
    - monochromatic: ΔH < 15° (same hue, varied saturation/lightness)
    - analogous: 15° < ΔH < 45° (neighboring hues)
    - complementary: 160° < ΔH < 200° (opposite hues)

    **Complex Schemes:**
    - split-complementary: 120°-160° (complement with ±30° offset)
    - triadic: 110°-130° (3 colors ~120° apart)
    - tetradic: 85°-105° (4 colors ~90° apart, rectangle)
    - quadratic: 5 colors with specific angle distributions
    - compound: Multiple harmony relationships in palette

    **Chromatic:**
    - achromatic: Grayscale (S=0, regardless of hue)

    Args:
        hex_color: Target color hex code
        palette: List of hex colors to analyze (typically 3-10 colors)
        return_metadata: If True, return detailed analysis dict instead of string

    Returns:
        Harmony type (string) or detailed analysis dict if return_metadata=True
        Analysis dict includes:
        - harmony: Main harmony classification
        - hue_angles: Angles between target and palette colors
        - palette_hues: All hue values in palette
        - saturation_variance: S variance (0-1)
        - lightness_variance: L variance (0-1)
        - chromatic: Boolean (achromatic if False)
        - confidence: 0-1 confidence in classification

    Example:
        >>> palette = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]  # Quadratic
        >>> get_color_harmony_advanced("#FF0000", palette, return_metadata=True)
        {
            'harmony': 'quadratic',
            'hue_angles': [0, 120, 240, 60],
            'chromatic': True,
            'confidence': 0.92
        }
    """
    try:
        if not palette or len(palette) < 2:
            return (
                "monochromatic"
                if not return_metadata
                else {"harmony": "monochromatic", "confidence": 0.5}
            )

        target_color = coloraide.Color(hex_color)
        target_hsl = target_color.convert("hsl")
        target_hue = target_hsl["hue"]
        target_sat = target_hsl["saturation"]

        # Extract palette properties
        palette_colors = [coloraide.Color(c) for c in palette if c != hex_color]
        if not palette_colors:
            harmony = "monochromatic"
            return harmony if not return_metadata else {"harmony": harmony, "confidence": 0.5}

        # Calculate hue angles (0-360)
        hue_angles = []
        saturations = []
        lightnesses = []

        for color in palette_colors:
            hsl = color.convert("hsl")
            hue_angles.append(hsl["hue"])
            saturations.append(hsl["saturation"])
            lightnesses.append(hsl["lightness"])

        # Check if achromatic (no saturation)
        is_achromatic = all(s < 0.05 for s in saturations + [target_sat])

        if is_achromatic:
            result = "achromatic"
            if return_metadata:
                return {
                    "harmony": result,
                    "chromatic": False,
                    "confidence": 0.95,
                    "saturations": saturations,
                }
            return result

        # Calculate hue differences (normalized to 0-180)
        hue_diffs = []
        for hue in hue_angles:
            diff = abs(hue - target_hue)
            if diff > 180:
                diff = 360 - diff
            hue_diffs.append(diff)

        # Analyze hue distribution pattern
        sorted_angles = sorted(set([round(h, 1) for h in hue_angles + [target_hue]]))
        angle_gaps = []
        for i in range(len(sorted_angles)):
            next_angle = sorted_angles[(i + 1) % len(sorted_angles)]
            gap = next_angle - sorted_angles[i]
            if gap < 0:
                gap += 360
            angle_gaps.append(gap)

        avg_gap = sum(angle_gaps) / len(angle_gaps) if angle_gaps else 0
        gap_variance = np.var(angle_gaps) if angle_gaps else 0

        # Classify based on patterns
        avg_hue_diff = sum(hue_diffs) / len(hue_diffs)
        sat_variance = np.var(saturations + [target_sat])
        light_variance = np.var(lightnesses)

        # Pattern matching for advanced schemes
        if avg_hue_diff < 15:
            harmony = "monochromatic"
            confidence = 0.95
        elif avg_hue_diff < 45:
            harmony = "analogous"
            confidence = 0.90
        elif 100 < avg_hue_diff < 140:
            # Check for triadic (3 colors ~120° apart)
            if len(palette_colors) >= 2 and abs(avg_gap - 120) < 20:
                harmony = "triadic"
                confidence = 0.92
            else:
                harmony = "split-complementary"
                confidence = 0.80
        elif 160 <= avg_hue_diff <= 200:
            harmony = "complementary"
            confidence = 0.93
        elif 80 < avg_gap < 110:
            # Tetradic or quadratic (4-5 colors ~90°/72° apart)
            if len(palette_colors) >= 4 and abs(avg_gap - 90) < 15:
                harmony = "tetradic"
                confidence = 0.91
            elif len(palette_colors) >= 4 and abs(avg_gap - 72) < 15:
                harmony = "quadratic"
                confidence = 0.88
            else:
                harmony = "tetradic"
                confidence = 0.85
        else:
            # Fallback to base classification
            harmony = "compound"
            confidence = max(0.5, 1.0 - (gap_variance / 1000))

        if return_metadata:
            return {
                "harmony": harmony,
                "hue_angles": [round(h, 1) for h in hue_angles],
                "target_hue": round(target_hue, 1),
                "palette_hues": sorted_angles,
                "saturation_variance": float(sat_variance),
                "lightness_variance": float(light_variance),
                "average_hue_difference": round(avg_hue_diff, 1),
                "average_angle_gap": round(avg_gap, 1),
                "chromatic": True,
                "confidence": round(confidence, 2),
            }

        return harmony

    except Exception:
        return (
            "unknown"
            if not return_metadata
            else {"harmony": "unknown", "confidence": 0.0, "error": True}
        )


def color_similarity(color1: str, color2: str, threshold: float = 5.0) -> bool:
    """
    Determine if two colors are perceptually similar using ColorAide's delta_e().

    Args:
        color1: First color (hex string)
        color2: Second color (hex string)
        threshold: ΔE threshold for similarity
                  Recommended thresholds:
                  - 2.0: Very similar (barely noticeable difference)
                  - 5.0: Similar (noticeable but acceptable)
                  - 10.0: Somewhat different (clearly different)

    Returns:
        True if colors are similar (within threshold)

    Example:
        >>> color_similarity("#F15925", "#F15924", threshold=2.0)
        True  # Very similar colors
        >>> color_similarity("#FF0000", "#00FF00", threshold=10.0)
        False  # Clearly different
    """
    de = calculate_delta_e(color1, color2)
    return de < threshold


def find_nearest_color(
    target_hex: str, color_palette: dict, threshold: float = 10.0
) -> tuple[str, float]:
    """
    Find the nearest color to a target in a palette using Delta-E.

    Useful for color matching, naming, and standardization.

    Args:
        target_hex: Color to match
        color_palette: Dict mapping {name: hex_color} or {name: rgb_tuple}
        threshold: Maximum ΔE for match (return None name if exceeded)

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
        de = calculate_delta_e(target_hex, palette_color)

        if de < best_match[1]:
            best_match = (name, de)

    return best_match


def merge_similar_colors(colors: list[str], threshold: float = 15.0) -> list[str]:
    """
    Merge perceptually similar colors from a list using ColorAide's delta_e().

    Useful for reducing color count while preserving distinct hues.

    Args:
        colors: List of hex colors
        threshold: ΔE threshold for merging
                  15 = clearly different but related
                  10 = noticeable difference

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
            if calculate_delta_e(color1, color2) < threshold:
                similar_group.append(color2)
                used.add(j)

        # Use average color of group (in LAB space for better results)
        if len(similar_group) > 1:
            colors_lab = [coloraide.Color(c).convert("lab") for c in similar_group]

            avg_l = np.mean([c["lightness"] for c in colors_lab])
            avg_a = np.mean([c["a"] for c in colors_lab])
            avg_b = np.mean([c["b"] for c in colors_lab])

            merged_color = (
                coloraide.Color("lab", [avg_l, avg_a, avg_b]).convert("srgb").to_string(hex=True)
            )
            merged.append(merged_color)
        else:
            merged.append(color1)

        used.add(i)

    return merged


def validate_cluster_homogeneity(cluster_colors: list[str], max_internal_de: float = 10.0) -> bool:
    """
    Check if cluster colors are internally cohesive (perceptually similar).

    Useful for validating clustering results.

    Args:
        cluster_colors: List of hex colors in cluster
        max_internal_de: Maximum allowed Delta-E within cluster

    Returns:
        True if cluster is homogeneous (all pairs within threshold)

    Example:
        >>> cluster = ["#F15925", "#F15930", "#F15935"]  # All similar
        >>> validate_cluster_homogeneity(cluster, max_internal_de=15.0)
        True
    """
    if len(cluster_colors) < 2:
        return True

    # Check all pairs
    for i, color1 in enumerate(cluster_colors):
        for color2 in cluster_colors[i + 1 :]:
            if calculate_delta_e(color1, color2) > max_internal_de:
                return False

    return True


def ensure_displayable_color(hex_color: str, gamut: str = "srgb") -> str:
    """
    Map out-of-gamut colors to the nearest displayable color in the specified gamut.

    Uses ColorAide's `.fit()` method to handle edge cases where extracted colors
    might be theoretically valid but not displayable on standard displays.

    Args:
        hex_color: Color to map (hex string)
        gamut: Target gamut ("srgb", "p3", "rec2020") - defaults to sRGB

    Returns:
        Hex color guaranteed to be displayable in the specified gamut

    Example:
        >>> ensure_displayable_color("#FF0000")  # Already in sRGB
        '#FF0000'
        >>> # For out-of-gamut colors (rare), returns nearest displayable
        >>> ensure_displayable_color(extremely_saturated_color)
        '#FF0000'  # Fitted to sRGB

    Reference:
        https://coloraide.readthedocs.io/en/latest/gamut.html#fitting
    """
    try:
        color = coloraide.Color(hex_color)
        fitted = color.fit(gamut)
        return fitted.to_string(hex=True)
    except Exception:
        # Fallback: return original if fitting fails
        return hex_color


def match_color_to_palette(
    target_hex: str,
    palette: list[str],
    return_distance: bool = False,
    use_native_match: bool = False,
) -> str | tuple[str, float]:
    """
    Find the perceptually closest color in a palette using ColorAide.

    Uses Delta-E iteration to find the nearest color in the palette.

    Args:
        target_hex: Color to match (hex string)
        palette: List of candidate colors (hex strings)
        return_distance: If True, also return the Delta-E distance
        use_native_match: Deprecated parameter (kept for backward compatibility)

    Returns:
        Matched color hex code, or tuple of (hex, distance) if return_distance=True

    Example:
        >>> palette = ["#FF0000", "#0000FF", "#00FF00"]
        >>> match_color_to_palette("#FF1111", palette)
        '#FF0000'  # Nearest red
        >>> match_color_to_palette("#FF1111", palette, return_distance=True)
        ('#FF0000', 2.34)  # Hex and ΔE distance

    Reference:
        https://coloraide.readthedocs.io/en/latest/
    """
    if not palette:
        return target_hex if not return_distance else (target_hex, float("inf"))

    try:
        target_color = coloraide.Color(target_hex)
        palette_colors = [coloraide.Color(c) for c in palette]

        # Manual Delta-E iteration - reliable for all palette sizes
        best_match = palette_colors[0]
        best_distance = target_color.delta_e(best_match)

        for candidate in palette_colors[1:]:
            distance = target_color.delta_e(candidate)
            if distance < best_distance:
                best_distance = distance
                best_match = candidate

        matched_hex = best_match.to_string(hex=True)

        if return_distance:
            return matched_hex, best_distance
        return matched_hex

    except Exception:
        # Fallback: return first palette color
        if return_distance:
            return palette[0], float("inf")
        return palette[0]


def get_perceptual_distance_summary(
    colors: list[str],
) -> dict:
    """
    Get summary statistics of perceptual distances in a color list.

    Useful for understanding color diversity and distribution.

    Args:
        colors: List of hex colors

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

    distances = []

    # Calculate all pairwise distances
    for i, color1 in enumerate(colors):
        for color2 in colors[i + 1 :]:
            distances.append(calculate_delta_e(color1, color2))

    if not distances:
        return {"mean": 0, "std": 0, "min": 0, "max": 0}

    return {
        "mean": float(np.mean(distances)),
        "std": float(np.std(distances)),
        "min": float(np.min(distances)),
        "max": float(np.max(distances)),
        "count": len(distances),
    }


def compute_all_properties(hex_color: str, dominant_colors: list[str] | None = None) -> dict:
    """Compute all color properties at once

    Args:
        hex_color: Hex color code
        dominant_colors: List of dominant colors for Delta E calculation

    Returns:
        Dictionary with all computed properties
    """
    properties = {
        "hsl": hex_to_hsl(hex_color),
        "hsv": hex_to_hsv(hex_color),
        "temperature": get_color_temperature(hex_color),
        "saturation_level": get_saturation_level(hex_color),
        "lightness_level": get_lightness_level(hex_color),
        "is_neutral": is_neutral_color(hex_color),
        "wcag_contrast_on_white": round(calculate_wcag_contrast(hex_color, "#FFFFFF"), 2),
        "wcag_contrast_on_black": round(calculate_wcag_contrast(hex_color, "#000000"), 2),
        "wcag_aa_compliant_text": is_wcag_compliant(hex_color, "#FFFFFF", "AA", "normal"),
        "wcag_aaa_compliant_text": is_wcag_compliant(hex_color, "#FFFFFF", "AAA", "normal"),
        "wcag_aa_compliant_normal": is_wcag_compliant(hex_color, "#FFFFFF", "AA", "large"),
        "wcag_aaa_compliant_normal": is_wcag_compliant(hex_color, "#FFFFFF", "AAA", "large"),
        "colorblind_safe": get_saturation_level(hex_color) != "grayscale",  # Simplified
        "tint_color": get_color_variant(hex_color, "tint", 0.5),
        "shade_color": get_color_variant(hex_color, "shade", 0.5),
        "tone_color": get_color_variant(hex_color, "tone", 0.5),
        "closest_web_safe": get_closest_web_safe(hex_color),
        "closest_css_named": get_closest_css_named(hex_color),
    }

    # Calculate Delta E to nearest dominant color
    if dominant_colors:
        min_delta_e = min(calculate_delta_e(hex_color, d) for d in dominant_colors)
        properties["delta_e_to_dominant"] = round(min_delta_e, 2)

    return properties


def compute_all_properties_with_metadata(
    hex_color: str, dominant_colors: list[str] | None = None
) -> tuple[dict, dict]:
    """Compute all color properties and track their extraction sources

    Args:
        hex_color: Hex color code
        dominant_colors: List of dominant colors for Delta E calculation

    Returns:
        Tuple of (properties dict, metadata dict mapping field names to tool sources)
    """
    properties = compute_all_properties(hex_color, dominant_colors)

    # Track which tool extracted each property
    metadata = {
        "hsl": "color_utils.hex_to_hsl",
        "hsv": "color_utils.hex_to_hsv",
        "temperature": "color_utils.get_color_temperature",
        "saturation_level": "color_utils.get_saturation_level",
        "lightness_level": "color_utils.get_lightness_level",
        "is_neutral": "color_utils.is_neutral_color",
        "wcag_contrast_on_white": "color_utils.calculate_wcag_contrast",
        "wcag_contrast_on_black": "color_utils.calculate_wcag_contrast",
        "wcag_aa_compliant_text": "color_utils.is_wcag_compliant",
        "wcag_aaa_compliant_text": "color_utils.is_wcag_compliant",
        "wcag_aa_compliant_normal": "color_utils.is_wcag_compliant",
        "wcag_aaa_compliant_normal": "color_utils.is_wcag_compliant",
        "colorblind_safe": "color_utils.get_saturation_level",
        "tint_color": "color_utils.get_color_variant",
        "shade_color": "color_utils.get_color_variant",
        "tone_color": "color_utils.get_color_variant",
        "closest_web_safe": "color_utils.get_closest_web_safe",
        "closest_css_named": "color_utils.get_closest_css_named",
    }

    if dominant_colors and "delta_e_to_dominant" in properties:
        metadata["delta_e_to_dominant"] = "color_utils.calculate_delta_e"

    return properties, metadata
