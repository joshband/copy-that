"""
Spacing Token Models

Pydantic models for spacing token extraction and processing.
Follows the pattern of color_extractor.py ExtractedColorToken.
"""

from enum import Enum

from pydantic import BaseModel, Field, computed_field


class SpacingScale(str, Enum):
    """Scale system classification for spacing tokens"""

    # Standard scales
    FOUR_POINT = "4pt"  # 4, 8, 12, 16, 20, 24...
    EIGHT_POINT = "8pt"  # 8, 16, 24, 32, 40...
    GOLDEN_RATIO = "golden"  # 1.618 multiplier
    FIBONACCI = "fibonacci"  # 1, 2, 3, 5, 8, 13...

    # Custom/detected
    LINEAR = "linear"  # Equal increments
    EXPONENTIAL = "exponential"  # Multiplied increments
    CUSTOM = "custom"  # Non-standard scale


class SpacingType(str, Enum):
    """Semantic classification of spacing usage"""

    # Layout spacing
    MARGIN = "margin"
    PADDING = "padding"
    GAP = "gap"

    # Component spacing
    INSET = "inset"  # Internal padding
    STACK = "stack"  # Vertical spacing between items
    INLINE = "inline"  # Horizontal spacing between items

    # Semantic spacing
    SECTION = "section"  # Between major sections
    COMPONENT = "component"  # Between components
    ELEMENT = "element"  # Between small elements

    # Special
    BORDER = "border"  # Border widths
    RADIUS = "radius"  # Border radius


class ResponsiveBreakpoint(str, Enum):
    """Standard responsive breakpoints"""

    XS = "xs"  # < 576px
    SM = "sm"  # >= 576px
    MD = "md"  # >= 768px
    LG = "lg"  # >= 992px
    XL = "xl"  # >= 1200px
    XXL = "xxl"  # >= 1400px


class SpacingToken(BaseModel):
    """
    Comprehensive spacing token with computed properties for design systems.

    Follows the ColorToken pattern from copy_that.application.color_extractor.

    Example:
        >>> token = SpacingToken(
        ...     value_px=16,
        ...     name="spacing-md",
        ...     semantic_role="padding",
        ...     confidence=0.92
        ... )
        >>> token.value_rem  # Computed: 1.0
        >>> token.css_variable  # Computed: "--spacing-md"
    """

    # Core Properties
    value_px: int = Field(..., ge=0, description="Spacing value in pixels")
    name: str = Field(..., description="Token name (e.g., 'spacing-md', 'gap-lg')")

    # Design Token Properties
    semantic_role: str | None = Field(
        None, description="DESIGN INTENT: Role Claude assigns (e.g., 'padding', 'margin', 'gap')"
    )
    spacing_type: SpacingType | None = Field(None, description="Classification of spacing usage")
    category: str | None = Field(
        None, description="Token category (e.g., 'layout', 'component', 'element')"
    )

    # Scale Properties
    scale_position: int | None = Field(
        None, ge=0, description="Position in scale (0=smallest, higher=larger)"
    )
    scale_system: SpacingScale | None = Field(
        None, description="Detected scale system (4pt, 8pt, golden, etc.)"
    )
    base_unit: int | None = Field(
        None, ge=1, description="Base unit of the scale (e.g., 4 for 4pt grid)"
    )

    # Confidence & Detection
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    count: int = Field(default=1, ge=1, description="Number of times detected")
    prominence_percentage: float | None = Field(
        None, ge=0, le=100, description="Percentage of elements using this spacing"
    )

    # Grid Compliance
    grid_aligned: bool | None = Field(
        None, description="Whether value aligns to detected grid system"
    )
    grid_deviation_px: int | None = Field(
        None, ge=0, description="Pixels away from nearest grid point"
    )

    # Responsive Properties
    responsive_scales: dict[str, int] | None = Field(
        None, description="Suggested values at breakpoints: {'sm': 12, 'md': 16, 'lg': 24}"
    )

    # Usage Contexts
    usage: list[str] = Field(
        default_factory=list, description="Suggested usage contexts (headers, cards, buttons, etc.)"
    )

    # Relationships
    related_tokens: list[str] | None = Field(None, description="Related token names in the scale")

    # Extraction Metadata
    extraction_metadata: dict | None = Field(
        None,
        description="Maps field names to extraction tool (e.g., {'scale_system': 'spacing_utils.detect_scale'})",
    )

    # Computed Properties
    @computed_field
    @property
    def value_rem(self) -> float:
        """Convert px to rem (assuming 16px base)"""
        return round(self.value_px / 16, 4)

    @computed_field
    @property
    def value_em(self) -> float:
        """Convert px to em (context-dependent, same as rem for base)"""
        return round(self.value_px / 16, 4)

    @computed_field
    @property
    def css_variable(self) -> str:
        """Generate CSS custom property name"""
        # Sanitize name for CSS variable
        safe_name = self.name.replace(" ", "-").lower()
        return f"--{safe_name}"

    @computed_field
    @property
    def tailwind_class(self) -> str | None:
        """Suggest closest Tailwind spacing class"""
        # Tailwind uses 0.25rem (4px) increments
        tailwind_value = self.value_px / 4
        if tailwind_value == int(tailwind_value):
            return (
                f"p-{int(tailwind_value)}"
                if self.spacing_type == SpacingType.PADDING
                else f"m-{int(tailwind_value)}"
            )
        return None


class SpacingExtractionResult(BaseModel):
    """Result of spacing extraction from an image"""

    tokens: list[SpacingToken] = Field(..., description="Extracted spacing tokens")
    scale_system: SpacingScale = Field(..., description="Detected overall scale system")
    base_unit: int = Field(..., description="Detected base unit in pixels")
    base_unit_confidence: float = Field(
        0.0, ge=0, le=1, description="How confident the extractor is in the base unit"
    )
    grid_compliance: float = Field(
        ..., ge=0, le=1, description="Percentage of values aligned to grid"
    )
    extraction_confidence: float = Field(
        ..., ge=0, le=1, description="Overall extraction confidence"
    )

    # Summary
    min_spacing: int = Field(..., description="Smallest spacing value detected")
    max_spacing: int = Field(..., description="Largest spacing value detected")
    unique_values: list[int] = Field(..., description="All unique spacing values")
    cv_gap_diagnostics: dict | None = Field(
        default=None,
        description="Cross-check of CV gaps against base spacing (dominant gap, deviation, tolerance).",
    )
    base_alignment: dict | None = Field(
        default=None,
        description="Comparison of expected vs inferred base spacing, when expected was provided.",
    )
    cv_gaps_sample: list[float] | None = Field(
        default=None, description="Sample of CV-measured gaps for QA/debug."
    )


# Convenience functions for common operations


def create_spacing_token(
    value_px: int, name: str | None = None, confidence: float = 0.85
) -> SpacingToken:
    """
    Quick function to create a spacing token with defaults.

    Args:
        value_px: Spacing value in pixels
        name: Optional token name (auto-generated if not provided)
        confidence: Confidence score

    Returns:
        SpacingToken with computed properties

    Example:
        >>> token = create_spacing_token(16)
        >>> token.name
        'spacing-16'
        >>> token.value_rem
        1.0
    """
    if name is None:
        name = f"spacing-{value_px}"

    return SpacingToken(value_px=value_px, name=name, confidence=confidence)


def from_rem(value_rem: float) -> int:
    """
    Convert rem to px (assuming 16px base).

    Args:
        value_rem: Value in rem units

    Returns:
        Value in pixels (rounded to nearest int)
    """
    return round(value_rem * 16)
