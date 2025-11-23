"""
Accessibility validation for design tokens.

Provides WCAG contrast ratio calculation and colorblind safety checks
for design tokens in the validation pipeline.
"""

import re
from enum import Enum

from pydantic import BaseModel

from copy_that.pipeline.exceptions import ValidationError
from copy_that.pipeline.types import TokenResult, TokenType


class WCAGLevel(str, Enum):
    """WCAG conformance levels."""

    A = "A"
    AA = "AA"
    AAA = "AAA"


class ColorblindType(str, Enum):
    """Types of color vision deficiency."""

    DEUTERANOPIA = "deuteranopia"  # Green-blind
    PROTANOPIA = "protanopia"  # Red-blind
    TRITANOPIA = "tritanopia"  # Blue-blind


class ContrastResult(BaseModel):
    """Result of a contrast check."""

    ratio: float
    passes_aa: bool
    passes_aaa: bool
    passes_aa_large: bool
    passes_aaa_large: bool


class AccessibilityCalculator:
    """
    Calculate accessibility metrics for color tokens.

    Implements WCAG 2.1 contrast ratio algorithms and
    colorblind simulation for safety checking.
    """

    # WCAG thresholds
    AA_NORMAL = 4.5
    AA_LARGE = 3.0
    AAA_NORMAL = 7.0
    AAA_LARGE = 4.5

    # Colorblind simulation matrices (simplified Brettel algorithm)
    # These matrices transform RGB colors to simulate colorblind vision
    COLORBLIND_MATRICES: dict[ColorblindType, list[list[float]]] = {
        ColorblindType.PROTANOPIA: [
            [0.567, 0.433, 0.0],
            [0.558, 0.442, 0.0],
            [0.0, 0.242, 0.758],
        ],
        ColorblindType.DEUTERANOPIA: [
            [0.625, 0.375, 0.0],
            [0.7, 0.3, 0.0],
            [0.0, 0.3, 0.7],
        ],
        ColorblindType.TRITANOPIA: [
            [0.95, 0.05, 0.0],
            [0.0, 0.433, 0.567],
            [0.0, 0.475, 0.525],
        ],
    }

    def _parse_hex_color(self, hex_color: str) -> tuple[int, int, int]:
        """
        Parse a hex color string to RGB values.

        Supports formats: #RGB, #RRGGBB, #RRGGBBAA, RGB, RRGGBB, RRGGBBAA

        Args:
            hex_color: Hex color string

        Returns:
            Tuple of (R, G, B) values (0-255)

        Raises:
            ValidationError: If hex color is invalid
        """
        if not hex_color:
            raise ValidationError("Empty hex color value")

        # Remove leading #
        color = hex_color.lstrip("#")

        # Validate hex characters
        if not re.match(r"^[0-9A-Fa-f]+$", color):
            raise ValidationError(
                f"Invalid hex color: {hex_color}",
                details={"color": hex_color},
            )

        # Handle different formats
        if len(color) == 3:
            # #RGB format
            r = int(color[0] * 2, 16)
            g = int(color[1] * 2, 16)
            b = int(color[2] * 2, 16)
        elif len(color) == 6:
            # #RRGGBB format
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
        elif len(color) == 8:
            # #RRGGBBAA format (ignore alpha)
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
        else:
            raise ValidationError(
                f"Invalid hex color length: {hex_color}",
                details={"color": hex_color, "length": len(color)},
            )

        return (r, g, b)

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """
        Convert RGB values to hex string.

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)

        Returns:
            Hex color string with leading #
        """
        # Clamp values to 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return f"#{r:02X}{g:02X}{b:02X}"

    def get_relative_luminance(self, hex_color: str) -> float:
        """
        Calculate relative luminance of a color (0-1).

        Uses the WCAG 2.1 formula with gamma correction.

        Args:
            hex_color: Hex color string

        Returns:
            Relative luminance value between 0 and 1
        """
        r, g, b = self._parse_hex_color(hex_color)

        # Convert to 0-1 range
        r_srgb = r / 255.0
        g_srgb = g / 255.0
        b_srgb = b / 255.0

        # Apply gamma correction
        def gamma_correct(value: float) -> float:
            if value <= 0.03928:
                return value / 12.92
            return float(((value + 0.055) / 1.055) ** 2.4)

        r_linear = gamma_correct(r_srgb)
        g_linear = gamma_correct(g_srgb)
        b_linear = gamma_correct(b_srgb)

        # Calculate luminance using ITU-R BT.709 coefficients
        return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

    def calculate_contrast_ratio(self, color1_hex: str, color2_hex: str) -> float:
        """
        Calculate WCAG contrast ratio between two colors.

        Uses relative luminance formula from WCAG 2.1.
        Returns ratio from 1:1 to 21:1.

        Args:
            color1_hex: First color as hex string
            color2_hex: Second color as hex string

        Returns:
            Contrast ratio (1.0 to 21.0)
        """
        l1 = self.get_relative_luminance(color1_hex)
        l2 = self.get_relative_luminance(color2_hex)

        # Ensure L1 is the lighter color
        if l1 < l2:
            l1, l2 = l2, l1

        # Calculate contrast ratio
        return (l1 + 0.05) / (l2 + 0.05)

    def check_wcag_compliance(
        self,
        ratio: float,
        level: WCAGLevel = WCAGLevel.AA,
        is_large_text: bool = False,
    ) -> bool:
        """
        Check if contrast ratio meets WCAG level.

        Args:
            ratio: Contrast ratio to check
            level: WCAG level (A, AA, or AAA)
            is_large_text: Whether text is large (18pt+ or 14pt+ bold)

        Returns:
            True if ratio meets the specified WCAG level
        """
        if level == WCAGLevel.A:
            # Level A has no contrast requirements
            return True
        elif level == WCAGLevel.AA:
            threshold = self.AA_LARGE if is_large_text else self.AA_NORMAL
        else:  # AAA
            threshold = self.AAA_LARGE if is_large_text else self.AAA_NORMAL

        return ratio >= threshold

    def check_contrast(self, color1_hex: str, color2_hex: str) -> ContrastResult:
        """
        Check contrast between two colors and return full result.

        Args:
            color1_hex: First color as hex string
            color2_hex: Second color as hex string

        Returns:
            ContrastResult with ratio and pass/fail for each WCAG level
        """
        ratio = self.calculate_contrast_ratio(color1_hex, color2_hex)

        return ContrastResult(
            ratio=ratio,
            passes_aa=ratio >= self.AA_NORMAL,
            passes_aaa=ratio >= self.AAA_NORMAL,
            passes_aa_large=ratio >= self.AA_LARGE,
            passes_aaa_large=ratio >= self.AAA_LARGE,
        )

    def simulate_colorblind(
        self,
        color_hex: str,
        colorblind_type: ColorblindType,
    ) -> str:
        """
        Simulate how a color appears to colorblind users.

        Uses transformation matrices to approximate colorblind vision.

        Args:
            color_hex: Color as hex string
            colorblind_type: Type of color blindness to simulate

        Returns:
            Simulated color as hex string
        """
        if not isinstance(colorblind_type, ColorblindType):
            raise ValidationError(
                f"Invalid colorblind type: {colorblind_type}",
                details={"type": str(colorblind_type)},
            )

        r, g, b = self._parse_hex_color(color_hex)

        # Normalize to 0-1
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        # Get transformation matrix
        matrix = self.COLORBLIND_MATRICES[colorblind_type]

        # Apply transformation
        new_r = matrix[0][0] * r_norm + matrix[0][1] * g_norm + matrix[0][2] * b_norm
        new_g = matrix[1][0] * r_norm + matrix[1][1] * g_norm + matrix[1][2] * b_norm
        new_b = matrix[2][0] * r_norm + matrix[2][1] * g_norm + matrix[2][2] * b_norm

        # Convert back to 0-255
        r_out = int(round(new_r * 255))
        g_out = int(round(new_g * 255))
        b_out = int(round(new_b * 255))

        return self._rgb_to_hex(r_out, g_out, b_out)

    def _calculate_color_distance(self, color1_hex: str, color2_hex: str) -> float:
        """
        Calculate Euclidean distance between two colors in RGB space.

        Args:
            color1_hex: First color as hex string
            color2_hex: Second color as hex string

        Returns:
            Distance value (0 to ~441 for max distance)
        """
        r1, g1, b1 = self._parse_hex_color(color1_hex)
        r2, g2, b2 = self._parse_hex_color(color2_hex)

        return float(((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5)

    def check_colorblind_safety(
        self,
        colors: list[str],
    ) -> dict[str, float]:
        """
        Check if a color palette is distinguishable for colorblind users.

        Calculates safety scores based on minimum color distance between
        any pair of colors when viewed by colorblind users.

        Args:
            colors: List of hex color strings

        Returns:
            Dictionary with safety scores (0-1) for each colorblind type
        """
        result: dict[str, float] = {}

        # Handle edge cases
        if len(colors) <= 1:
            for cb_type in ColorblindType:
                result[cb_type.value] = 1.0
            return result

        # Maximum possible RGB distance (black to white)
        max_distance = (255**2 + 255**2 + 255**2) ** 0.5  # ~441

        for cb_type in ColorblindType:
            # Simulate all colors for this colorblind type
            simulated = [self.simulate_colorblind(c, cb_type) for c in colors]

            # Find minimum distance between any pair
            min_distance = max_distance
            for i in range(len(simulated)):
                for j in range(i + 1, len(simulated)):
                    distance = self._calculate_color_distance(simulated[i], simulated[j])
                    min_distance = min(min_distance, distance)

            # Convert to 0-1 score
            # Use a threshold where ~50 distance units = 0.5 score
            # This means colors need reasonable separation to be considered safe
            score = min(1.0, min_distance / 100.0)
            result[cb_type.value] = score

        return result

    def calculate_accessibility_score(
        self,
        token: TokenResult,
        background_color: str = "#FFFFFF",
    ) -> float:
        """
        Calculate overall accessibility score for a color token.

        Combines WCAG contrast into a 0-1 score.
        Returns 1.0 for non-color tokens.

        Args:
            token: TokenResult to evaluate
            background_color: Background color for contrast calculation

        Returns:
            Accessibility score between 0 and 1
        """
        # Return 1.0 for non-color tokens
        if token.token_type != TokenType.COLOR:
            return 1.0

        # Get the color value
        value = token.value

        # Handle non-string values (like dicts for gradients)
        if not isinstance(value, str):
            return 1.0

        # Validate it looks like a hex color
        color = value.lstrip("#")
        if not re.match(r"^[0-9A-Fa-f]{3,8}$", color):
            raise ValidationError(
                f"Invalid color value for accessibility check: {value}",
                details={"token_name": token.name, "value": value},
            )

        # Calculate contrast ratio
        ratio = self.calculate_contrast_ratio(value, background_color)

        # Convert ratio to 0-1 score
        # Score formula:
        # - ratio 1:1 = 0.0 (no contrast)
        # - ratio 4.5:1 = 0.5 (passes AA)
        # - ratio 7:1 = 0.75 (passes AAA)
        # - ratio 21:1 = 1.0 (maximum contrast)

        # Normalize to 0-1 using log scale for better distribution
        # ratio ranges from 1 to 21
        import math

        max_ratio = 21.0
        min_ratio = 1.0

        # Use logarithmic scaling for more intuitive scores
        log_ratio = math.log(ratio)
        log_max = math.log(max_ratio)
        log_min = math.log(min_ratio)

        score = (log_ratio - log_min) / (log_max - log_min)

        return max(0.0, min(1.0, score))
