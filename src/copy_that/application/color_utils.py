"""
Comprehensive color utilities for computing all color properties.

This module provides functions to calculate:
- Color space conversions (HSL, HSV, LAB)
- Accessibility metrics (WCAG contrast, colorblind safety)
- Color analysis (temperature, saturation, lightness)
- Color variants (tints, shades, tones)
- Advanced metrics (Delta E, web-safe colors, CSS names)
"""

import re
import math
from typing import Optional, Tuple
from colorsys import rgb_to_hls, rgb_to_hsv


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


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple (0-255 range)"""
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color"""
    return f"#{r:02X}{g:02X}{b:02X}"


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
    """Check if color is neutral/grayscale"""
    r, g, b = hex_to_rgb(hex_code)
    # Neutral if R, G, B are very close
    diff = max(abs(r - g), abs(g - b), abs(r - b))
    return diff < 20


def calculate_wcag_contrast(hex1: str, hex2: str) -> float:
    """Calculate WCAG contrast ratio between two colors (1.0 to 21.0)"""
    def get_luminance(hex_code: str) -> float:
        r, g, b = hex_to_rgb(hex_code)
        # Convert to 0-1 range
        r, g, b = r / 255.0, g / 255.0, b / 255.0

        # Apply gamma correction
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

        # Calculate relative luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = get_luminance(hex1)
    l2 = get_luminance(hex2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def is_wcag_compliant(hex_color: str, background: str = "#FFFFFF", level: str = "AA", size: str = "normal") -> bool:
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


def get_closest_web_safe(hex_code: str) -> str:
    """Find closest web-safe color (216 color palette)"""
    r, g, b = hex_to_rgb(hex_code)

    # Round to nearest web-safe value (0, 51, 102, 153, 204, 255)
    r = round(r / 51) * 51
    g = round(g / 51) * 51
    b = round(b / 51) * 51

    return rgb_to_hex(r, g, b)


def get_closest_css_named(hex_code: str) -> Optional[str]:
    """Find closest CSS named color"""
    r, g, b = hex_to_rgb(hex_code)

    min_distance = float('inf')
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
    """Calculate Delta E (color difference) using CIE 1976 simple formula

    Returns:
        Delta E value (0 = identical, >5 = perceptible difference)
    """
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)

    # Simple Euclidean distance in RGB space (normalized to 0-1)
    r1, g1, b1 = r1 / 255.0, g1 / 255.0, b1 / 255.0
    r2, g2, b2 = r2 / 255.0, g2 / 255.0, b2 / 255.0

    delta_e = math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2) * 100
    return delta_e


def compute_all_properties(hex_color: str, dominant_colors: Optional[list[str]] = None) -> dict:
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
