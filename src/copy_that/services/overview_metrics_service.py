"""Service for inferring overview metrics from extracted tokens.

Analyzes color, spacing, typography, and shadow tokens to provide insights
about the design system maturity, organization, characteristics, aesthetic
movement, emotional tone, and design complexity.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class ElaboratedMetric:
    """A metric with primary value and multiple elaboration options."""

    def __init__(self, primary: str, elaborations: list[str]):
        self.primary = primary
        self.elaborations = elaborations  # Alternative descriptions/subcategories


class OverviewMetrics:
    """Inferred metrics about a design system based on extracted tokens."""

    def __init__(self):
        self.spacing_scale_system: str | None = None
        self.spacing_uniformity: float = 0.0  # 0-1 how well tokens fit a consistent scale
        self.color_harmony_type: str | None = None  # complementary, analogous, triadic, etc.
        self.color_palette_type: str | None = None  # monochromatic, limited, rich, etc.
        self.color_temperature: str | None = None  # warm, cool, balanced
        self.typography_hierarchy_depth: int = 0  # Number of distinct font size levels
        self.typography_scale_type: str | None = None  # linear, modular, custom
        self.design_system_maturity: str = "emerging"  # emerging, developing, mature, comprehensive
        self.token_organization_quality: str = "basic"  # basic, organized, highly_organized

        # NEW: Enhanced metrics with elaboration
        self.art_movement: ElaboratedMetric | None = None  # Design era/movement classification
        self.emotional_tone: ElaboratedMetric | None = None  # Emotional character
        self.design_complexity: ElaboratedMetric | None = None  # System complexity level
        self.saturation_character: ElaboratedMetric | None = None  # Color vibrancy character
        self.temperature_profile: ElaboratedMetric | None = None  # Thermal personality
        self.design_system_insight: ElaboratedMetric | None = None  # Overall DS assessment

        self.insights: list[str] = []  # Human-readable insight strings


def infer_metrics(
    colors: Sequence[Any],
    spacing: Sequence[Any],
    typography: Sequence[Any],
    shadows: Sequence[Any] | None = None,
) -> OverviewMetrics:
    """Infer design system metrics from extracted tokens.

    Args:
        colors: Color tokens
        spacing: Spacing tokens
        typography: Typography tokens
        shadows: Shadow tokens (optional)

    Returns:
        OverviewMetrics with inferred insights
    """
    metrics = OverviewMetrics()

    if colors:
        _analyze_color_system(colors, metrics)
    if spacing:
        _analyze_spacing_system(spacing, metrics)
    if typography:
        _analyze_typography_system(typography, metrics)
    if shadows:
        _analyze_shadow_system(shadows, metrics)

    _assess_overall_maturity(colors, spacing, typography, metrics)

    # NEW: Enhanced multi-dimensional analysis
    if colors:
        _infer_art_movement(colors, metrics)
        _infer_emotional_tone(colors, metrics)
        _infer_saturation_character(colors, metrics)
        _infer_temperature_profile(colors, metrics)

    _infer_design_complexity(colors, spacing, typography, metrics)
    _infer_design_system_insight(colors, spacing, typography, metrics)

    return metrics


def _analyze_color_system(colors: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Analyze color tokens to infer palette characteristics."""
    if not colors:
        return

    # Extract hex values
    hex_values: list[str] = []
    for color in colors:
        hex_val = getattr(color, "hex", None) or (
            color.raw.get("$value") if isinstance(color, dict) and "$value" in color.raw else None
        )
        if hex_val and isinstance(hex_val, str):
            hex_values.append(hex_val.lstrip("#").upper())

    if not hex_values:
        return

    # Determine palette type based on count
    color_count = len(hex_values)
    if color_count == 1:
        metrics.color_palette_type = "monochromatic"
        metrics.insights.append("Single color palette - minimal variety")
    elif color_count <= 3:
        metrics.color_palette_type = "limited"
        metrics.insights.append("Limited color palette - focused and minimal")
    elif color_count <= 8:
        metrics.color_palette_type = "structured"
        metrics.insights.append("Structured color palette - well-organized")
    elif color_count <= 15:
        metrics.color_palette_type = "rich"
        metrics.insights.append("Rich color palette - comprehensive system")
    else:
        metrics.color_palette_type = "comprehensive"
        metrics.insights.append("Comprehensive color palette - extensive variety")

    # Analyze temperature
    warm_count = _count_warm_colors(hex_values)
    cool_count = _count_cool_colors(hex_values)

    if warm_count > cool_count * 1.5:
        metrics.color_temperature = "warm"
        metrics.insights.append("Warm color temperature - energetic and inviting")
    elif cool_count > warm_count * 1.5:
        metrics.color_temperature = "cool"
        metrics.insights.append("Cool color temperature - calm and professional")
    else:
        metrics.color_temperature = "balanced"
        metrics.insights.append("Balanced temperature - neutral and versatile")

    # Analyze saturation
    avg_saturation = _calculate_average_saturation(hex_values)
    if avg_saturation > 70:
        metrics.insights.append("Vibrant and saturated colors - high visual impact")
    elif avg_saturation < 30:
        metrics.insights.append("Muted and desaturated colors - sophisticated and subdued")


def _analyze_spacing_system(spacing: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Analyze spacing tokens to infer scale system."""
    if not spacing:
        return

    values: list[int] = []
    for token in spacing:
        val_px = getattr(token, "value_px", None)
        if val_px is not None:
            values.append(int(val_px))
        elif isinstance(token, dict) and isinstance(token.raw, dict):
            val_str = token.raw.get("$value", "")
            if isinstance(val_str, str) and val_str.endswith("px"):
                try:
                    values.append(int(val_str.replace("px", "")))
                except (ValueError, TypeError):
                    pass

    if not values:
        return

    values = sorted(set(values))

    # Detect scale system
    scale_type = _detect_spacing_scale(values)
    metrics.spacing_scale_system = scale_type

    if scale_type == "4pt":
        metrics.insights.append("4-point grid system - fine-grained control")
        metrics.spacing_uniformity = 0.95
    elif scale_type == "8pt":
        metrics.insights.append("8-point grid system - standard and balanced")
        metrics.spacing_uniformity = 0.9
    elif scale_type == "golden":
        metrics.insights.append("Golden ratio spacing - mathematical harmony")
        metrics.spacing_uniformity = 0.85
    elif scale_type == "fibonacci":
        metrics.insights.append("Fibonacci spacing - natural progression")
        metrics.spacing_uniformity = 0.8
    else:
        metrics.insights.append(f"Custom spacing scale ({len(values)} distinct values)")
        metrics.spacing_uniformity = 0.5


def _analyze_typography_system(typography: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Analyze typography tokens to infer hierarchy."""
    if not typography:
        return

    font_sizes: set[int] = set()
    for token in typography:
        size = getattr(token, "font_size", None)
        if size is not None:
            font_sizes.add(int(size))
        elif isinstance(token, dict) and isinstance(token.raw, dict):
            size_str = token.raw.get("$value", {}).get("fontSize", "")
            if isinstance(size_str, str) and size_str.endswith("px"):
                try:
                    font_sizes.add(int(size_str.replace("px", "")))
                except (ValueError, TypeError):
                    pass

    if font_sizes:
        metrics.typography_hierarchy_depth = len(font_sizes)
        if len(font_sizes) <= 2:
            metrics.typography_scale_type = "minimal"
            metrics.insights.append("Minimal typography - 1-2 font sizes")
        elif len(font_sizes) <= 5:
            metrics.typography_scale_type = "moderate"
            metrics.insights.append(f"Moderate typography hierarchy - {len(font_sizes)} font sizes")
        else:
            metrics.typography_scale_type = "extensive"
            metrics.insights.append(
                f"Extensive typography hierarchy - {len(font_sizes)} font sizes"
            )


def _analyze_shadow_system(shadows: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Analyze shadow tokens."""
    if not shadows:
        return

    shadow_count = len(shadows)
    if shadow_count <= 2:
        metrics.insights.append(f"Minimal shadow system ({shadow_count} shadow preset)")
    elif shadow_count <= 5:
        metrics.insights.append(f"Shadow depth system ({shadow_count} presets)")
    else:
        metrics.insights.append(f"Comprehensive shadow library ({shadow_count} presets)")


def _assess_overall_maturity(
    colors: Sequence[Any],
    spacing: Sequence[Any],
    typography: Sequence[Any],
    metrics: OverviewMetrics,
) -> None:
    """Assess overall design system maturity based on token coverage."""
    has_colors = len(colors) > 0
    has_spacing = len(spacing) > 0
    has_typography = len(typography) > 0

    category_count = sum([has_colors, has_spacing, has_typography])

    if category_count == 0:
        metrics.design_system_maturity = "emerging"
        metrics.token_organization_quality = "basic"
    elif category_count == 1:
        metrics.design_system_maturity = "emerging"
        metrics.token_organization_quality = (
            "organized" if len(colors) > 5 or len(spacing) > 5 or len(typography) > 3 else "basic"
        )
    elif category_count == 2:
        metrics.design_system_maturity = "developing"
        metrics.token_organization_quality = "organized"
    else:
        total_tokens = len(colors) + len(spacing) + len(typography)
        if total_tokens > 30:
            metrics.design_system_maturity = "mature"
            metrics.token_organization_quality = "highly_organized"
        else:
            metrics.design_system_maturity = "developing"
            metrics.token_organization_quality = "organized"


def _count_warm_colors(hex_values: list[str]) -> int:
    """Count warm colors (reds, oranges, yellows)."""
    warm = 0
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                b = int(hex_val[4:6], 16)
                if (r - b) > 20:  # More red/warm
                    warm += 1
            except ValueError:
                pass
    return warm


def _count_cool_colors(hex_values: list[str]) -> int:
    """Count cool colors (blues, purples, greens)."""
    cool = 0
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                b = int(hex_val[4:6], 16)
                if (b - r) > 20:  # More blue/cool
                    cool += 1
            except ValueError:
                pass
    return cool


def _calculate_average_saturation(hex_values: list[str]) -> float:
    """Calculate average saturation of colors (0-100)."""
    saturations: list[float] = []
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16) / 255
                g = int(hex_val[2:4], 16) / 255
                b = int(hex_val[4:6], 16) / 255

                max_c = max(r, g, b)
                min_c = min(r, g, b)
                saturation = (max_c - min_c) / max_c if max_c > 0 else 0
                saturations.append(saturation * 100)
            except ValueError:
                pass
    return sum(saturations) / len(saturations) if saturations else 50.0


def _detect_spacing_scale(values: list[int]) -> str:
    """Detect the spacing scale system used."""
    if not values or len(values) < 2:
        return "custom"

    sorted_vals = sorted(values)

    # Check for 4-point grid
    if all(v % 4 == 0 for v in sorted_vals):
        return "4pt"

    # Check for 8-point grid
    if all(v % 8 == 0 for v in sorted_vals):
        return "8pt"

    # Check for Fibonacci
    fib_sequence = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    if all(v in fib_sequence for v in sorted_vals):
        return "fibonacci"

    # Check for Golden Ratio (approximately 1.618x)
    if len(sorted_vals) >= 2:
        ratios = []
        for i in range(len(sorted_vals) - 1):
            if sorted_vals[i] > 0:
                ratio = sorted_vals[i + 1] / sorted_vals[i]
                ratios.append(ratio)
        if ratios and all(1.5 < r < 1.7 for r in ratios):
            return "golden"

    return "custom"


# ============================================================================
# ENHANCED METRICS INFERENCE - Multi-dimensional Design Analysis
# ============================================================================


def _infer_art_movement(colors: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Infer design era and aesthetic movement from color patterns."""
    hex_values: list[str] = _extract_hex_values(colors)
    if not hex_values:
        return

    color_count = len(hex_values)
    avg_sat = _calculate_average_saturation(hex_values)
    avg_lightness = _calculate_average_lightness(hex_values)
    warm_count = _count_warm_colors(hex_values)
    cool_count = _count_cool_colors(hex_values)
    has_neon = _detect_neon_colors(hex_values)
    has_muted = _detect_muted_colors(hex_values)
    has_pastels = _detect_pastel_colors(hex_values)

    # Complex heuristic-based classification
    primary_movement = "Contemporary"
    elaborations: list[str] = []

    # Minimalism: very limited, desaturated (check first - most specific)
    if color_count <= 2 and avg_sat < 40:
        primary_movement = "Minimalism"
        elaborations = [
            "Ultra-refined restraint",
            "Essentialist principle",
            "Maximum impact, minimal means",
            "Negative space as design language",
            "Zen-like focus and clarity",
        ]
    # Monochromatic: single color, varying lightness
    elif color_count == 1 or (color_count <= 3 and (warm_count == 0 or cool_count == 0)):
        primary_movement = "Monochromatic"
        elaborations = [
            "Single-hue color progression",
            "Tonal depth and hierarchy",
            "Extreme visual harmony",
            "Sophisticated color discipline",
            "Calming unified identity",
        ]
    # Brutalism: intentional high-contrast minimal palette (nearly pure B/W + possibly one accent)
    elif (
        color_count <= 3
        and avg_sat < 30  # Very desaturated (almost grayscale)
        and (avg_lightness < 20 or avg_lightness > 80)  # Extreme lightness
        and _calculate_lightness_variance(hex_values) > 2000  # Large difference between light/dark
    ):
        primary_movement = "Brutalism"
        elaborations = [
            "Stark geometric minimalism",
            "High-contrast typography-focused",
            "Utilitarian and bold",
            "Raw materialist expression",
            "Functional over ornamental",
        ]
    # Cyberpunk / Synthwave: neon + dark background, high contrast
    elif has_neon and avg_lightness < 50 and color_count >= 3:
        primary_movement = "Cyberpunk / Synthwave"
        elaborations = [
            "Neon-against-dark aesthetics",
            "Retro-futuristic techno glow",
            "80s-90s digital rebellion",
            "Electric neon rebellion",
            "Digital noir atmosphere",
        ]
    # Vaporwave / Aesthetic: neon + pastels, high saturation, nostalgic
    elif has_neon and has_pastels and avg_lightness > 60 and avg_sat > 50:
        primary_movement = "Vaporwave / Aesthetic"
        elaborations = [
            "Neon-pastel dream fusion",
            "90s-00s nostalgic surrealism",
            "Glitchy utopian nostalgia",
            "Post-digital dreaming",
            "Transient digital culture",
        ]
    # Retro-Futurism: warm + cool balance, 50s-70s style
    elif 1.5 < warm_count / max(cool_count, 1) < 4 and 40 < avg_sat < 75 and color_count >= 4:
        primary_movement = "Retro-Futurism"
        elaborations = [
            "1950s-1970s sci-fi aesthetic",
            "Space-race optimism and wonder",
            "Chrome-and-plastic modernism",
            "Atomic age revivalism",
            "Golden Age of design futurism",
        ]
    # Mid-Century Modern: balanced, organized, sophisticated (check before Swiss Style)
    elif color_count >= 4 and 30 < avg_sat < 60 and 40 < avg_lightness < 70:
        primary_movement = "Mid-Century Modern"
        elaborations = [
            "Dieter Rams / Braun minimalism",
            "Functional grid-based elegance",
            "Purposeful industrial design",
            "Eames-era organic modernism",
            "Timeless Scandinavian restraint",
        ]
    # Swiss Style / International Typographic: clean, organized, ordered (check after Mid-Century)
    elif color_count <= 5 and avg_sat < 40 and avg_lightness > 30:
        primary_movement = "Swiss Style"
        elaborations = [
            "Grid-based precision",
            "Helvetica-era modernism",
            "Information-first hierarchy",
            "Universal geometric order",
            "Functional clarity",
        ]
    # Art Deco: geometric balance, metallic/gold hints
    elif color_count >= 4 and avg_sat > 60 and _has_metallic_hints(hex_values):
        primary_movement = "Art Deco"
        elaborations = [
            "Geometric symmetry and precision",
            "Luxury and glamour maximalism",
            "Ornamental sophistication",
            "1920s-1930s opulence",
            "Jazz-age geometric exuberance",
        ]
    # Art Nouveau: organic, flowing, nature-inspired
    elif color_count >= 5 and 50 < avg_sat < 75 and warm_count > cool_count:
        primary_movement = "Art Nouveau"
        elaborations = [
            "Organic flowing curves",
            "Nature-inspired elegance",
            "1890s-1910s naturalism",
            "Botanical and biomorphic forms",
            "Sensuous organic beauty",
        ]
    # Dark Academia: muted, jewel-toned palette
    elif has_muted and color_count >= 5 and _has_jewel_tones(hex_values):
        primary_movement = "Dark Academia"
        elaborations = [
            "Jewel-toned sophistication",
            "Moody and intellectual",
            "Heritage luxury aesthetic",
            "Vintage library ambiance",
            "Mysterious scholarly elegance",
        ]
    # Contemporary CGI Analog Fetishism: high contrast, very saturated
    elif color_count >= 4 and avg_sat > 75 and has_neon:
        primary_movement = "CGI Analog Fetishism"
        elaborations = [
            "Highly polished 3D aesthetics",
            "Speculative hardware design",
            "Photorealistic idealization",
            "Rendered product fantasy",
            "Hyper-saturated digital realism",
        ]
    # Maximalism: high color count, high saturation, complex
    elif color_count >= 12 and avg_sat > 60:
        primary_movement = "Maximalism"
        elaborations = [
            "Exuberant complexity and abundance",
            "Rich polychromatic richness",
            "Layered visual density",
            "Post-minimalist abundance",
            "Maximally expressive color symphony",
        ]
    # Pastel Dream: light, desaturated, soft
    elif has_pastels and avg_lightness > 75 and avg_sat < 50:
        primary_movement = "Pastel Dream"
        elaborations = [
            "Soft and whimsical aesthetics",
            "Gentle color harmony",
            "Contemporary cottagecore vibes",
            "Ethereal and dreamlike palette",
            "Soothing delicate color language",
        ]
    # Flat Design: moderate saturation, clean colors
    elif 3 <= color_count <= 8 and 50 < avg_sat < 70 and not has_neon:
        primary_movement = "Flat Design"
        elaborations = [
            "Digital-native aesthetic",
            "Clean geometric forms",
            "Application UI-centric",
            "Post-skeuomorphism modernism",
            "Accessibility-focused clarity",
        ]
    # High Contrast Accessibility: distinct lightness values
    elif avg_lightness < 30 or avg_lightness > 80:
        primary_movement = "High Contrast Accessibility"
        elaborations = [
            "WCAG AAA compliance-conscious",
            "Visual clarity prioritized",
            "Inclusive design approach",
            "Distinction-focused palette",
            "Accessible contrast hierarchy",
        ]
    # Earthy / Organic: warm muted tones, nature-inspired
    elif warm_count > cool_count and avg_sat < 60 and color_count >= 4:
        primary_movement = "Earthy / Organic"
        elaborations = [
            "Nature-inspired earth tones",
            "Rustic and grounded aesthetic",
            "Sustainable design sensibility",
            "Terracotta and clay vibrancy",
            "Biophilic color grounding",
        ]

    metrics.art_movement = ElaboratedMetric(primary_movement, elaborations)


def _infer_emotional_tone(colors: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Infer emotional character based on saturation + lightness, not marketing copy."""
    hex_values: list[str] = _extract_hex_values(colors)
    if not hex_values:
        return

    avg_lightness = _calculate_average_lightness(hex_values)
    avg_sat = _calculate_average_saturation(hex_values)
    temp_ratio = _calculate_weighted_temperature_ratio(hex_values)

    primary_tone = "Balanced"
    elaborations: list[str] = []

    # Muted + light = soft, accessible, understated
    if avg_sat < 45 and avg_lightness > 60:
        primary_tone = "Soft & Accessible"
        elaborations = [
            "Gentle, desaturated palette",
            "Low visual intensity",
            "Calming and approachable",
        ]
    # High saturation + warm = energetic, inviting
    elif avg_sat > 60 and temp_ratio > 0.6:
        primary_tone = "Energetic & Inviting"
        elaborations = [
            "Warm, saturated colors",
            "High visual engagement",
            "Stimulating and approachable",
        ]
    # High saturation + cool = playful, bold
    elif avg_sat > 65 and temp_ratio < 0.4:
        primary_tone = "Playful & Bold"
        elaborations = [
            "Cool, saturated colors",
            "High contrast and impact",
            "Modern and expressive",
        ]
    # Muted + dark = professional, serious
    elif avg_sat < 45 and avg_lightness < 45:
        primary_tone = "Professional & Serious"
        elaborations = [
            "Muted, sophisticated palette",
            "Low-key visual presence",
            "Trustworthy and reserved",
        ]
    # Mixed saturation, balanced temperature = versatile, neutral
    elif avg_sat > 45 and abs(temp_ratio - 0.5) < 0.15:
        primary_tone = "Balanced & Versatile"
        elaborations = [
            "Mixed warm and cool accents",
            "Moderate saturation",
            "Adaptable to various contexts",
        ]
    else:
        primary_tone = "Balanced"
        elaborations = [
            "Mixed characteristics",
            "Context-dependent reading",
            "Versatile visual presence",
        ]

    metrics.emotional_tone = ElaboratedMetric(primary_tone, elaborations)


def _infer_saturation_character(colors: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Infer vibrancy and color intensity character."""
    hex_values: list[str] = _extract_hex_values(colors)
    if not hex_values:
        return

    avg_sat = _calculate_average_saturation(hex_values)

    primary_character = "Moderate"
    elaborations: list[str] = []

    if avg_sat > 80:
        primary_character = "Hyper-Saturated"
        elaborations = [
            "Intense chromatic purity",
            "Maximum visual impact",
            "Eye-catching vibrancy",
        ]
    elif avg_sat > 65:
        primary_character = "Vivid & Saturated"
        elaborations = [
            "Rich chromatic richness",
            "High visual energy",
            "Bold color expression",
        ]
    elif avg_sat > 45:
        primary_character = "Balanced Saturation"
        elaborations = [
            "Natural color harmony",
            "Refined equilibrium",
            "Accessible vibrancy",
        ]
    elif avg_sat > 25:
        primary_character = "Muted & Subdued"
        elaborations = [
            "Soft chromatic restraint",
            "Sophisticated greyness",
            "Reduced visual intensity",
        ]
    else:
        primary_character = "Desaturated & Refined"
        elaborations = [
            "Monochromatic tendencies",
            "Minimalist color economy",
            "Grayscale sophistication",
        ]

    metrics.saturation_character = ElaboratedMetric(primary_character, elaborations)


def _infer_temperature_profile(colors: Sequence[Any], metrics: OverviewMetrics) -> None:
    """Infer thermal personality using saturation-weighted warm/cool distribution."""
    hex_values: list[str] = _extract_hex_values(colors)
    if not hex_values:
        return

    # Use saturation-weighted temperature ratio (0=cool, 0.5=balanced, 1=warm)
    temp_ratio = _calculate_weighted_temperature_ratio(hex_values)

    primary_profile = "Balanced"
    elaborations: list[str] = []

    if temp_ratio > 0.65:
        primary_profile = "Warm Dominant"
        elaborations = [
            "Solar and inviting atmosphere",
            "Approachable and comforting",
            "Stimulating warmth",
        ]
    elif temp_ratio < 0.35:
        primary_profile = "Cool Dominant"
        elaborations = [
            "Lunar and serene atmosphere",
            "Professional coolness",
            "Calming influence",
        ]
    elif abs(temp_ratio - 0.5) < 0.1:
        primary_profile = "Balanced Thermal"
        elaborations = [
            "Harmonious temperature equilibrium",
            "Mixed warm and cool accents",
            "Versatile thermal character",
        ]
    else:
        primary_profile = "Warm-Leaning" if temp_ratio > 0.5 else "Cool-Leaning"
        elaborations = [
            f"Slight thermal preference toward {'warmth' if temp_ratio > 0.5 else 'coolness'}",
            "Mixed color temperature character",
            "Flexible thermal personality",
        ]

    metrics.temperature_profile = ElaboratedMetric(primary_profile, elaborations)


def _infer_design_complexity(
    colors: Sequence[Any],
    spacing: Sequence[Any],
    typography: Sequence[Any],
    metrics: OverviewMetrics,
) -> None:
    """Infer overall design system complexity."""
    color_count = len(colors) if colors else 0
    spacing_count = len(spacing) if spacing else 0
    typography_count = len(typography) if typography else 0
    total_tokens = color_count + spacing_count + typography_count

    primary_level = "Minimal"
    elaborations: list[str] = []

    if total_tokens == 0:
        primary_level = "Non-Existent"
        elaborations = ["No extracted tokens", "System foundation needed", "Blank slate"]
    elif total_tokens <= 5:
        primary_level = "Ultra-Minimal"
        elaborations = [
            "Extreme simplification",
            "Bare essentials only",
            "Proof-of-concept stage",
        ]
    elif total_tokens <= 15:
        primary_level = "Minimal"
        elaborations = [
            "Essential components only",
            "Lean and focused",
            "Early-stage foundation",
        ]
    elif total_tokens <= 30:
        primary_level = "Moderate"
        elaborations = [
            "Well-rounded system foundation",
            "Core categories covered",
            "Room for expansion",
        ]
    elif total_tokens <= 60:
        primary_level = "Complex"
        elaborations = [
            "Comprehensive token coverage",
            "Multi-tier refinement",
            "Production-ready scope",
        ]
    else:
        primary_level = "Highly Complex"
        elaborations = [
            "Extensive design vocabulary",
            "Enterprise-scale tokens",
            "Advanced system maturity",
        ]

    metrics.design_complexity = ElaboratedMetric(primary_level, elaborations)


def _infer_design_system_insight(
    colors: Sequence[Any],
    spacing: Sequence[Any],
    typography: Sequence[Any],
    metrics: OverviewMetrics,
) -> None:
    """Infer overall design system quality and assessment."""
    color_count = len(colors) if colors else 0
    spacing_count = len(spacing) if spacing else 0
    typography_count = len(typography) if typography else 0

    has_all_categories = color_count > 0 and spacing_count > 0 and typography_count > 0
    well_organized = color_count > 3 and spacing_count > 3 and typography_count > 2
    comprehensive = color_count > 8 and spacing_count > 5 and typography_count > 4

    primary_insight = "Foundation Stage"
    elaborations: list[str] = []

    if not has_all_categories:
        primary_insight = "Incomplete System"
        elaborations = [
            "Missing key token categories",
            "Selective focus area",
            "Ready for expansion",
        ]
    elif comprehensive:
        primary_insight = "Mature Design System"
        elaborations = [
            "Comprehensive token ecosystem",
            "Multi-dimensional consistency",
            "Production-ready platform",
        ]
    elif well_organized:
        primary_insight = "Well-Organized System"
        elaborations = [
            "Solid foundational tokens",
            "Clear organizational intent",
            "Ready for scaling",
        ]
    else:
        primary_insight = "Emerging System"
        elaborations = [
            "Foundation tokens in place",
            "Coherent starting point",
            "Growing consistency",
        ]

    metrics.design_system_insight = ElaboratedMetric(primary_insight, elaborations)


# ============================================================================
# UTILITY FUNCTIONS FOR ENHANCED ANALYSIS
# ============================================================================


def _calculate_lightness_variance(hex_values: list[str]) -> float:
    """Calculate variance in lightness values (0-100 range)."""
    lightnesses: list[float] = []
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16) / 255
                g = int(hex_val[2:4], 16) / 255
                b = int(hex_val[4:6], 16) / 255
                max_c = max(r, g, b)
                min_c = min(r, g, b)
                lightness = (max_c + min_c) / 2 * 100
                lightnesses.append(lightness)
            except ValueError:
                pass

    if not lightnesses or len(lightnesses) < 2:
        return 0.0

    mean = sum(lightnesses) / len(lightnesses)
    variance = sum((x - mean) ** 2 for x in lightnesses) / len(lightnesses)
    return variance


def _calculate_saturation_variance(hex_values: list[str]) -> float:
    """Calculate variance in saturation values (0-100 range)."""
    saturations: list[float] = []
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16) / 255
                g = int(hex_val[2:4], 16) / 255
                b = int(hex_val[4:6], 16) / 255

                max_c = max(r, g, b)
                min_c = min(r, g, b)
                saturation = (max_c - min_c) / max_c if max_c > 0 else 0
                saturations.append(saturation * 100)
            except ValueError:
                pass

    if not saturations or len(saturations) < 2:
        return 0.0

    mean = sum(saturations) / len(saturations)
    variance = sum((x - mean) ** 2 for x in saturations) / len(saturations)
    return variance


def _calculate_weighted_temperature_ratio(hex_values: list[str]) -> float:
    """Calculate warm/cool ratio weighted by saturation.

    Returns value between 0 and 1:
    - 0 = fully cool
    - 0.5 = balanced
    - 1 = fully warm
    """
    warm_sat_sum = 0.0
    cool_sat_sum = 0.0

    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)

                # Calculate saturation
                r_norm = r / 255
                g_norm = g / 255
                b_norm = b / 255
                max_c = max(r_norm, g_norm, b_norm)
                min_c = min(r_norm, g_norm, b_norm)
                saturation = (max_c - min_c) / max_c if max_c > 0 else 0

                # Classify as warm or cool based on R-B delta
                if (r - b) > 20:
                    warm_sat_sum += saturation
                elif (b - r) > 20:
                    cool_sat_sum += saturation
                # else: neutral, doesn't contribute
            except ValueError:
                pass

    total = warm_sat_sum + cool_sat_sum
    if total == 0:
        return 0.5  # Balanced if no warm/cool colors

    return warm_sat_sum / total


def _extract_hex_values(colors: Sequence[Any]) -> list[str]:
    """Extract hex values from color tokens."""
    hex_values: list[str] = []
    for color in colors:
        hex_val = getattr(color, "hex", None) or (
            color.raw.get("$value") if isinstance(color, dict) and "$value" in color.raw else None
        )
        if hex_val and isinstance(hex_val, str):
            hex_values.append(hex_val.lstrip("#").upper())
    return hex_values


def _calculate_average_lightness(hex_values: list[str]) -> float:
    """Calculate average lightness (0-100) of colors."""
    lightnesses: list[float] = []
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16) / 255
                g = int(hex_val[2:4], 16) / 255
                b = int(hex_val[4:6], 16) / 255

                max_c = max(r, g, b)
                min_c = min(r, g, b)
                lightness = (max_c + min_c) / 2
                lightnesses.append(lightness * 100)
            except ValueError:
                pass
    return sum(lightnesses) / len(lightnesses) if lightnesses else 50.0


def _detect_neon_colors(hex_values: list[str]) -> bool:
    """Detect if palette includes neon/fluorescent colors."""
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)

                # Neon: very high saturation in one channel with high brightness
                max_channel = max(r, g, b)
                min_channel = min(r, g, b)
                if max_channel > 200 and (max_channel - min_channel) > 150:
                    return True
            except ValueError:
                pass
    return False


def _detect_muted_colors(hex_values: list[str]) -> bool:
    """Detect if palette is primarily muted/desaturated."""
    avg_sat = _calculate_average_saturation(hex_values)
    return avg_sat < 40


def _detect_pastel_colors(hex_values: list[str]) -> bool:
    """Detect if palette includes pastel colors."""
    pastel_count = 0
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)

                # Pastels: high lightness (>70%), moderate saturation
                avg = (r + g + b) / 3 / 255 * 100
                if avg > 70:
                    pastel_count += 1
            except ValueError:
                pass

    return pastel_count > len(hex_values) * 0.3


def _has_metallic_hints(hex_values: list[str]) -> bool:
    """Detect if palette has metallic/gold hints."""
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)

                # Gold-like: R > G > B with R-B delta
                if r > g > b and r - b > 50 and r > 150:
                    return True
            except ValueError:
                pass
    return False


def _has_jewel_tones(hex_values: list[str]) -> bool:
    """Detect if palette has jewel tones (emerald, sapphire, amethyst, etc)."""
    jewel_count = 0
    for hex_val in hex_values:
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)

                # Jewel tones: deep, saturated, one channel dominant
                max_channel = max(r, g, b)
                min_channel = min(r, g, b)

                # Check if it's a deep jewel tone (low lightness + high saturation)
                lightness = (max_channel + min_channel) / 2 / 255 * 100
                saturation = (max_channel - min_channel) / max_channel if max_channel > 0 else 0

                if lightness < 60 and saturation > 0.4:
                    jewel_count += 1
            except ValueError:
                pass

    return jewel_count > len(hex_values) * 0.3
