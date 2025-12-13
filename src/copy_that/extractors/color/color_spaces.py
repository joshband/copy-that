"""
Advanced color space conversions using ColorAide library.

Provides utilities for:
- Oklch (perceptually uniform)
- OkLab (improved CIELAB)
- HSLuv (perceptually uniform HSL)
- CIEDE2000 color distance
- Hue analysis and color naming

Author: Copy This Research
Date: 2025-11-16
"""

import numpy as np

try:
    from coloraide import Color
except ImportError:
    raise ImportError("coloraide library required. Install with: pip install coloraide>=4.4.0")


class OklchColor:
    """Wrapper for Oklch color space operations with perceptual uniformity."""

    def __init__(self, hex_color: str):
        """Initialize from hex color."""
        self.color = Color(hex_color).convert("oklch")
        self.lightness = self.color["lightness"]
        self.chroma = self.color["chroma"]
        self.hue = self.color["hue"]
        self.hex = hex_color

    def to_hex(self) -> str:
        """Convert to hex string."""
        return self.color.convert("srgb").to_string(hex=True)

    def to_rgb(self) -> tuple[int, int, int]:
        """Convert to RGB (0-255)."""
        rgb = self.color.convert("srgb")
        return tuple(int(round(c * 255)) for c in rgb.coords())

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "OklchColor":
        """Create from RGB (0-255)."""
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        return cls(hex_color)

    def modify_lightness(self, new_lightness: float) -> "OklchColor":
        """Create new color with different lightness, preserving hue/chroma."""
        new_color = Color("oklch", [new_lightness, self.chroma, self.hue])
        return OklchColor(new_color.convert("srgb").to_string(hex=True))

    def modify_chroma(self, new_chroma: float) -> "OklchColor":
        """Create new color with different chroma, preserving hue/lightness."""
        new_color = Color("oklch", [self.lightness, new_chroma, self.hue])
        return OklchColor(new_color.convert("srgb").to_string(hex=True))

    def rotate_hue(self, degrees: float) -> "OklchColor":
        """Create new color with rotated hue."""
        new_hue = (self.hue + degrees) % 360
        new_color = Color("oklch", [self.lightness, self.chroma, new_hue])
        return OklchColor(new_color.convert("srgb").to_string(hex=True))


def generate_oklch_scale(
    base_hex: str, scale_levels: dict[str, float] | None = None
) -> dict[str, str]:
    """
    Generate color scale (50-900) with perceptually uniform lightness using Oklch.

    This is the recommended method for scale generation as it produces
    visually consistent steps compared to HSL-based scaling.

    Args:
        base_hex: Base color hex (typically 500 level)
        scale_levels: Optional dict mapping level names to lightness values (0-1)
                     Default: Standard 50-900 scale

    Returns:
        Dict mapping level names to hex colors

    Example:
        >>> scale = generate_oklch_scale("#F15925")
        >>> scale["50"]   # Very light
        >>> scale["500"]  # Base color
        >>> scale["900"]  # Very dark
    """
    if scale_levels is None:
        scale_levels = {
            "50": 0.95,
            "100": 0.90,
            "200": 0.80,
            "300": 0.70,
            "400": 0.60,
            "500": None,  # Will use base
            "600": 0.40,
            "700": 0.30,
            "800": 0.20,
            "900": 0.10,
        }

    base_oklch = OklchColor(base_hex)

    # Use base lightness for level 500 if not specified
    if scale_levels["500"] is None:
        scale_levels["500"] = base_oklch.lightness

    scale = {}
    for level, lightness in scale_levels.items():
        # Create new color in Oklch space with modified lightness
        color = Color("oklch", [lightness, base_oklch.chroma, base_oklch.hue])
        scale[level] = color.convert("srgb").to_string(hex=True)

    return scale


def generate_oklch_variations(
    base_hex: str, variations: dict[str, tuple[float, float]] | None = None
) -> dict[str, str]:
    """
    Generate color variations by modifying chroma and hue.

    Useful for creating related colors while maintaining perceptual consistency.

    Args:
        base_hex: Base color
        variations: Dict mapping name to (chroma_factor, hue_rotation_degrees)
                   Default: complementary, analogous, triadic variations

    Returns:
        Dict mapping variation names to hex colors

    Example:
        >>> variations = generate_oklch_variations("#F15925")
        >>> variations["complementary"]  # 180° hue rotation
        >>> variations["saturated"]      # Increased chroma
    """
    if variations is None:
        variations = {
            "original": (1.0, 0),
            "desaturated": (0.5, 0),
            "saturated": (1.5, 0),
            "lighter": (1.0, 0),  # Handled separately
            "darker": (1.0, 0),  # Handled separately
            "complement": (1.0, 180),
            "analogous_warm": (1.0, 30),
            "analogous_cool": (1.0, -30),
            "triadic_1": (1.0, 120),
            "triadic_2": (1.0, 240),
        }

    base_oklch = OklchColor(base_hex)
    result = {}

    for name, (chroma_factor, hue_rotation) in variations.items():
        new_chroma = base_oklch.chroma * chroma_factor
        new_chroma = max(0, min(new_chroma, 0.4))  # Clamp to valid range

        new_hue = (base_oklch.hue + hue_rotation) % 360

        color = Color("oklch", [base_oklch.lightness, new_chroma, new_hue])
        result[name] = color.convert("srgb").to_string(hex=True)

    return result


def analyze_color_oklch(hex_color: str) -> dict:
    """
    Analyze color properties in multiple color spaces.

    Useful for understanding color characteristics for naming and categorization.

    Args:
        hex_color: Color to analyze

    Returns:
        Dict with properties in Oklch, OkLab, HSLuv spaces
    """
    color = Color(hex_color)

    oklch = color.convert("oklch")
    oklab = color.convert("oklab")
    hsluv = color.convert("hsluv")
    lab = color.convert("lab")

    return {
        "hex": hex_color,
        "oklch": {
            "lightness": round(oklch["lightness"], 3),
            "chroma": round(oklch["chroma"], 3),
            "hue": round(oklch["hue"], 1),
        },
        "oklab": {
            "lightness": round(oklab["lightness"], 3),
            "a": round(oklab["a"], 3),
            "b": round(oklab["b"], 3),
        },
        "cielab": {
            "lightness": round(lab["lightness"], 1),
            "a": round(lab["a"], 1),
            "b": round(lab["b"], 1),
            "chroma": round(np.sqrt(lab["a"] ** 2 + lab["b"] ** 2), 1),
        },
        "hsluv": {
            "hue": round(hsluv["hue"], 1),
            "saturation": round(hsluv["saturation"], 1),
            "lightness": round(hsluv["lightness"], 1),
        },
    }


def rgb_to_hsluv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """
    Convert RGB to HSLuv (perceptually uniform HSL).

    HSLuv is better for color perception than HSL while maintaining
    the intuitive hue/saturation/lightness model.

    Args:
        r, g, b: RGB values (0-255)

    Returns:
        Tuple of (hue, saturation, lightness) in HSLuv space
    """
    color = Color("srgb", [r / 255, g / 255, b / 255]).convert("hsluv")
    return (color["hue"], color["saturation"], color["lightness"])


def hsluv_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """Convert HSLuv to RGB (0-255)."""
    color = Color("hsluv", [h, s, l]).convert("srgb")
    return tuple(int(round(c * 255)) for c in color.coords())


def get_hue_family(hue: float) -> str:
    """
    Get color family name from hue (0-360 degrees).

    Args:
        hue: Hue angle in degrees

    Returns:
        Color family name (red, orange, yellow, green, cyan, blue, purple, pink)
    """
    hue = hue % 360

    if hue < 15 or hue >= 345:
        return "red"
    elif 15 <= hue < 45:
        return "orange"
    elif 45 <= hue < 75:
        return "yellow"
    elif 75 <= hue < 165:
        return "green"
    elif 165 <= hue < 255:
        return "blue"
    elif 255 <= hue < 315:
        return "purple"
    else:  # 315-345
        return "pink"


def categorize_saturation(saturation: float, space: str = "hsluv") -> str:
    """
    Categorize saturation level.

    Args:
        saturation: Saturation value (0-100 for HSLuv, 0-1 for Oklch)
        space: Color space used ("hsluv" or "oklch")

    Returns:
        Saturation category
    """
    if space == "hsluv":
        if saturation < 10:
            return "desaturated"
        elif saturation < 30:
            return "muted"
        elif saturation < 60:
            return "balanced"
        elif saturation < 80:
            return "saturated"
        else:
            return "vivid"
    else:  # oklch chroma
        if saturation < 0.05:
            return "desaturated"
        elif saturation < 0.15:
            return "muted"
        elif saturation < 0.25:
            return "balanced"
        elif saturation < 0.35:
            return "saturated"
        else:
            return "vivid"


def categorize_lightness(lightness: float) -> str:
    """
    Categorize lightness level (0-1 scale).

    Args:
        lightness: Lightness value (0-1)

    Returns:
        Lightness category
    """
    if lightness < 0.2:
        return "very-dark"
    elif lightness < 0.4:
        return "dark"
    elif lightness < 0.6:
        return "medium"
    elif lightness < 0.8:
        return "light"
    else:
        return "very-light"


def get_temperature(hue: float) -> str:
    """
    Determine if color is warm, cool, or neutral based on hue.

    Args:
        hue: Hue angle in degrees (0-360)

    Returns:
        Temperature category ("warm", "cool", or "neutral")
    """
    hue = hue % 360
    if hue < 60 or hue > 300:
        return "warm"  # Reds, oranges, yellows, pinks
    elif 120 <= hue <= 240:
        return "cool"  # Greens, cyans, blues, purples
    else:
        return "neutral"


# Backward compatibility: Make HSL scale generation use Oklch
def generate_color_scale_oklch_compatible(base_hex: str) -> dict[str, str]:
    """
    Generate color scale - compatible replacement for HSL-based scaling.

    Use this to replace the old `generate_color_scale()` function.
    """
    return generate_oklch_scale(base_hex)
