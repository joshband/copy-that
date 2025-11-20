"""
Semantic color naming using heuristic strategies.

Generates human-readable color names based on:
- Hue (red, orange, blue, etc.)
- Temperature (warm, cool, neutral)
- Saturation (vibrant, muted, desaturated)
- Lightness (dark, light, medium)
- Emotional associations

Naming styles:
- "simple": Just color name (e.g., "orange")
- "descriptive": Detailed name (e.g., "warm-orange-light")
- "emotional": Mood-based names (e.g., "vibrant-coral")
- "material": Material Design naming (e.g., "red-500")

Author: Copy This Research
Date: 2025-11-16
"""

from typing import Optional, Dict, Tuple
import numpy as np

try:
    from coloraide import Color
except ImportError:
    raise ImportError(
        "coloraide library required. Install with: pip install coloraide>=4.4.0"
    )


class SemanticColorNamer:
    """Heuristic-based semantic color naming system."""

    # Hue family definitions (in degrees)
    HUE_FAMILIES = {
        "red": (345, 15),
        "orange": (15, 45),
        "yellow": (45, 75),
        "yellow-green": (75, 105),
        "green": (105, 165),
        "cyan": (165, 195),
        "blue": (195, 255),
        "purple": (255, 315),
        "magenta": (315, 345),
    }

    def __init__(self):
        """Initialize color namer."""
        pass

    def name_color(
        self,
        hex_color: str,
        style: str = "descriptive",
        include_emotion: bool = False
    ) -> str:
        """
        Generate semantic color name.

        Args:
            hex_color: Color to name (e.g., "#F15925")
            style: Naming style
                - "simple": Just color name
                - "descriptive": Temperature + hue + lightness
                - "emotional": Mood-based
                - "technical": Hue family, saturation, lightness
                - "vibrancy": Vibrancy-focused (e.g., "vibrant-orange", "muted-blue")
            include_emotion: Add emotional descriptor to descriptive names

        Returns:
            Human-readable color name

        Example:
            >>> namer = SemanticColorNamer()
            >>> namer.name_color("#F15925", style="simple")
            'orange'
            >>> namer.name_color("#F15925", style="descriptive")
            'warm-orange-light'
            >>> namer.name_color("#F15925", style="emotional")
            'vibrant-coral'
            >>> namer.name_color("#F15925", style="vibrancy")
            'vibrant-orange'
        """
        color = Color(hex_color)
        oklch = color.convert("oklch")

        h = oklch["hue"]
        c = oklch["chroma"]
        l = oklch["lightness"]

        # Get base properties
        hue_name = self._get_hue_name(h)
        temperature = self._get_temperature(h)
        saturation_level = self._get_saturation_level(c)
        lightness_level = self._get_lightness_level(l)
        vibrancy_level = self._get_vibrancy_level(c, l)
        is_grayscale = c < 0.05

        if style == "simple":
            # Just the color name
            return hue_name

        elif style == "descriptive":
            # Build descriptive name
            parts = []

            # Add temperature (unless grayscale)
            if not is_grayscale and temperature != "neutral":
                parts.append(temperature)

            # Add hue
            parts.append(hue_name)

            # Add lightness level (unless medium)
            if lightness_level != "medium":
                parts.append(lightness_level)

            # Optionally add emotion
            if include_emotion and not is_grayscale:
                emotion = self._get_emotion(h, c, l)
                return f"{emotion}-{hue_name}"

            return "-".join(parts)

        elif style == "emotional":
            # Mood-based naming using vibrancy-aware emotions
            emotion = self._get_vibrancy_emotion(c, l)
            if emotion and hue_name:
                return f"{emotion}-{hue_name}"
            return f"{emotion}" if emotion else hue_name

        elif style == "technical":
            # Technical property listing
            parts = [hue_name]

            if saturation_level != "balanced":
                parts.append(saturation_level)

            if lightness_level != "medium":
                parts.append(lightness_level)

            return "-".join(parts)

        elif style == "vibrancy":
            # Vibrancy-focused naming
            if is_grayscale:
                # Use lightness descriptors for grayscale
                if lightness_level in ["very-dark", "dark"]:
                    return f"dark-{hue_name}"
                elif lightness_level in ["very-light", "light"]:
                    return f"light-{hue_name}"
                return hue_name
            else:
                # Combine vibrancy descriptor with hue
                if vibrancy_level and vibrancy_level != "moderate":
                    return f"{vibrancy_level}-{hue_name}"
                return hue_name

        else:
            return hue_name

    def analyze_color(self, hex_color: str) -> Dict:
        """
        Analyze all color properties for detailed understanding.

        Args:
            hex_color: Color to analyze

        Returns:
            Dict with comprehensive color properties
        """
        color = Color(hex_color)
        oklch = color.convert("oklch")
        hsl = color.convert("hsl")
        lab = color.convert("lab")

        h = oklch["hue"]
        c = oklch["chroma"]
        l = oklch["lightness"]

        # Calculate vibrancy
        vibrancy_score = self._calculate_vibrancy(c, l)
        vibrancy_level = self._get_vibrancy_level(c, l)

        return {
            "hex": hex_color,
            "hue_family": self._get_hue_family_name(h),
            "hue_angle": round(h, 1),
            "temperature": self._get_temperature(h),
            "saturation_level": self._get_saturation_level(c),
            "saturation_oklch": round(c, 3),
            "saturation_hsl": round(hsl["saturation"] * 100, 1),  # Convert to percentage
            "lightness_level": self._get_lightness_level(l),
            "lightness_oklch": round(l, 3),
            "lightness_hsl": round(hsl["lightness"] * 100, 1),  # Convert to percentage
            "brightness_lab": round(lab["lightness"], 1),
            "vibrancy_score": round(vibrancy_score, 3),
            "vibrancy_level": vibrancy_level,
            "is_grayscale": c < 0.05,
            "is_pastel": l > 0.8 and c < 0.15,
            "is_vibrant": vibrancy_score > 0.25,
            "emotion": self._get_emotion(h, c, l),
            "vibrancy_emotion": self._get_vibrancy_emotion(c, l),
            "names": {
                "simple": self.name_color(hex_color, style="simple"),
                "descriptive": self.name_color(hex_color, style="descriptive"),
                "emotional": self.name_color(hex_color, style="emotional"),
                "technical": self.name_color(hex_color, style="technical"),
                "vibrancy": self.name_color(hex_color, style="vibrancy"),
            }
        }

    def _get_hue_family_name(self, hue: float) -> str:
        """Get hue family name (more granular than _get_hue_name)."""
        hue = hue % 360

        for family, (start, end) in self.HUE_FAMILIES.items():
            if start <= hue < end:
                return family

        return "red"  # Default

    def _get_hue_name(self, hue: float) -> str:
        """Get main hue name (simplified to 6 colors)."""
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
            return "magenta"

    def _get_temperature(self, hue: float) -> str:
        """
        Determine if color is warm, cool, or neutral.

        Warm: Reds, oranges, yellows, pinks (0-60° and 300-360°)
        Cool: Greens, cyans, blues, purples (120-240°)
        Neutral: In between
        """
        hue = hue % 360

        if hue < 60 or hue > 300:
            return "warm"
        elif 120 <= hue <= 240:
            return "cool"
        else:
            return "neutral"

    def _get_saturation_level(self, chroma: float) -> str:
        """
        Get saturation level from Oklch chroma (0-0.4 range).

        Args:
            chroma: Oklch chroma value (0-1, but typically 0-0.4)

        Returns:
            Saturation category
        """
        if chroma < 0.05:
            return "desaturated"
        elif chroma < 0.15:
            return "muted"
        elif chroma < 0.25:
            return "balanced"
        elif chroma < 0.35:
            return "saturated"
        else:
            return "vivid"

    def _get_lightness_level(self, lightness: float) -> str:
        """
        Get lightness level from Oklch lightness (0-1 range).

        Args:
            lightness: Oklch lightness value (0-1)

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

    def _calculate_vibrancy(self, chroma: float, lightness: float) -> float:
        """
        Calculate vibrancy score (same formula as color_services.py).

        Vibrancy combines chroma (saturation) and lightness.
        Most vibrant colors have high chroma AND medium lightness (0.4-0.7).

        Args:
            chroma: Oklch chroma (0-0.4 typical range)
            lightness: Oklch lightness (0-1)

        Returns:
            Vibrancy score (0.0 to ~0.4, higher = more vibrant)
        """
        # Lightness factor peaks at L=0.5, decreases toward 0 and 1
        lightness_factor = 1.0 - (4.0 * (lightness - 0.5) ** 2)
        lightness_factor = max(0.0, lightness_factor)

        vibrancy = chroma * lightness_factor
        return vibrancy

    def _get_vibrancy_level(self, chroma: float, lightness: float) -> str:
        """
        Get vibrancy level from chroma and lightness.

        Args:
            chroma: Oklch chroma value
            lightness: Oklch lightness value

        Returns:
            Vibrancy category
        """
        vibrancy = self._calculate_vibrancy(chroma, lightness)

        if vibrancy < 0.05:
            return "dull"
        elif vibrancy < 0.15:
            return "muted"
        elif vibrancy < 0.25:
            return "moderate"
        elif vibrancy < 0.35:
            return "vibrant"
        else:
            return "electric"

    def _get_vibrancy_emotion(self, chroma: float, lightness: float) -> str:
        """
        Get vibrancy-aware emotional descriptor.

        Enhanced version of _get_emotion() that uses vibrancy scoring
        for more nuanced emotional naming.

        Args:
            chroma: Oklch chroma (0-1)
            lightness: Oklch lightness (0-1)

        Returns:
            Emotional descriptor based on vibrancy
        """
        vibrancy = self._calculate_vibrancy(chroma, lightness)
        is_grayscale = chroma < 0.05

        # Grayscale emotions
        if is_grayscale:
            if lightness < 0.25:
                return "shadowy"
            elif lightness < 0.5:
                return "smoky"
            elif lightness < 0.75:
                return "misty"
            else:
                return "cloudy"

        # Vibrancy-based emotions
        if vibrancy >= 0.35:
            return "electric"
        elif vibrancy >= 0.25:
            if lightness > 0.6:
                return "radiant"
            else:
                return "vivid"
        elif vibrancy >= 0.15:
            if lightness > 0.7:
                return "soft"
            elif lightness < 0.3:
                return "rich"
            else:
                return "balanced"
        elif vibrancy >= 0.05:
            if lightness > 0.7:
                return "pale"
            elif lightness < 0.3:
                return "dusky"
            else:
                return "muted"
        else:
            if lightness > 0.6:
                return "faded"
            else:
                return "subdued"

    def _get_emotion(self, hue: float, chroma: float, lightness: float) -> str:
        """
        Get emotional descriptor based on color properties.

        Combines hue, chroma, and lightness to suggest mood.

        Args:
            hue: Hue angle (0-360°)
            chroma: Oklch chroma (0-1)
            lightness: Oklch lightness (0-1)

        Returns:
            Emotional descriptor
        """
        # Grayscale emotions
        if chroma < 0.05:
            if lightness < 0.3:
                return "mysterious"
            elif lightness < 0.6:
                return "neutral"
            else:
                return "serene"

        # High saturation + high lightness
        if chroma > 0.3 and lightness > 0.5:
            return "vibrant"

        # High lightness + moderate saturation
        if lightness > 0.7 and chroma < 0.25:
            return "soft"

        # Low lightness + high saturation
        if lightness < 0.3 and chroma > 0.2:
            return "deep"

        # Medium saturation
        if 0.15 < chroma < 0.25:
            if lightness > 0.6:
                return "balanced"
            else:
                return "grounded"

        # High saturation
        if chroma > 0.25:
            return "bold"

        # Low saturation
        if chroma < 0.15:
            if lightness > 0.6:
                return "calm"
            else:
                return "muted"

        return "subtle"


# Material Design color naming utilities
class MaterialColorNamer:
    """Map colors to Material Design naming convention."""

    # Simplified Material Design palette
    # In real implementation, would use complete palette
    MATERIAL_COLORS = {
        "red": {
            "50": "#FFEBEE",
            "100": "#FFCDD2",
            "200": "#EF9A9A",
            "300": "#E57373",
            "400": "#EF5350",
            "500": "#F44336",
            "600": "#E53935",
            "700": "#D32F2F",
            "800": "#C62828",
            "900": "#B71C1C",
        },
        "orange": {
            "50": "#FFF3E0",
            "100": "#FFE0B2",
            "200": "#FFCC80",
            "300": "#FFB74D",
            "400": "#FFA726",
            "500": "#FF9800",
            "600": "#FB8C00",
            "700": "#F57C00",
            "800": "#E65100",
            "900": "#E65100",
        },
        # ... more colors
    }

    @staticmethod
    def find_nearest_material_color(
        hex_color: str,
        tolerance: float = 10.0
    ) -> Tuple[Optional[str], Optional[str], float]:
        """
        Find nearest Material Design color.

        Args:
            hex_color: Color to match
            tolerance: Maximum ΔE for match

        Returns:
            Tuple of (family, level, delta_e) or (None, None, tolerance+1)

        Example:
            >>> family, level, de = find_nearest_material_color("#F15925")
            >>> print(f"{family}-{level}: ΔE={de:.2f}")
            'orange-500: ΔE=3.45'
        """
        from delta_e import delta_e_2000

        best_family = None
        best_level = None
        best_distance = tolerance + 1

        for family, levels in MaterialColorNamer.MATERIAL_COLORS.items():
            for level, material_color in levels.items():
                de = delta_e_2000(hex_color, material_color)

                if de < best_distance:
                    best_distance = de
                    best_family = family
                    best_level = level

        if best_distance <= tolerance:
            return best_family, best_level, best_distance
        else:
            return None, None, best_distance


def name_color(hex_color: str, style: str = "descriptive") -> str:
    """
    Convenience function for single color naming.

    Example:
        >>> name_color("#F15925")
        'warm-orange-light'
    """
    namer = SemanticColorNamer()
    return namer.name_color(hex_color, style=style)


def analyze_color(hex_color: str) -> Dict:
    """
    Convenience function for color analysis.

    Example:
        >>> analysis = analyze_color("#F15925")
        >>> print(analysis["emotion"])
        'vibrant'
    """
    namer = SemanticColorNamer()
    return namer.analyze_color(hex_color)
