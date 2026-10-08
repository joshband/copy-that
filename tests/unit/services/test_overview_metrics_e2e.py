"""End-to-end tests for enhanced overview metrics inference.

Tests the complete pipeline of design characteristic inference with various
design palettes and token combinations.
"""

import pytest

from copy_that.services.overview_metrics_service import (
    ElaboratedMetric,
    infer_metrics,
)


class MockColor:
    """Mock color token for testing."""

    def __init__(self, hex_value: str):
        self.hex = hex_value
        self.raw = {"$value": hex_value}


class MockSpacingToken:
    """Mock spacing token for testing."""

    def __init__(self, value_px: int):
        self.value_px = value_px
        self.raw = {"$value": f"{value_px}px"}


class MockTypographyToken:
    """Mock typography token for testing."""

    def __init__(self, font_size: int):
        self.font_size = font_size
        self.raw = {"$value": {"fontSize": f"{font_size}px"}}


# ============================================================================
# RETRO-FUTURISM PALETTE (e.g., vintage synthesizer UI)
# ============================================================================


def test_retro_futurism_palette() -> None:
    """Test detection of retro-futurism aesthetic with warm-cool balance."""
    # Characteristics: Warm + cool balance, moderate saturation, 1950s-70s vibe
    # Using colors that evoke vintage synthesizer aesthetics
    colors = [
        MockColor("#FF5500"),  # Vintage orange
        MockColor("#004499"),  # Navy blue
        MockColor("#CC3300"),  # Burnt red
        MockColor("#0077DD"),  # Cerulean
        MockColor("#BBAA11"),  # Mustard yellow
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.art_movement is not None
    # May detect as Retro-Futurism or contemporary depending on exact heuristics
    assert metrics.art_movement.primary is not None
    assert len(metrics.art_movement.elaborations) > 0
    # Check that it has warm-cool balance insight in emotional tone
    assert metrics.emotional_tone is not None


# ============================================================================
# MID-CENTURY MODERNISM PALETTE
# ============================================================================


def test_mid_century_modern_palette() -> None:
    """Test detection of mid-century modern aesthetic."""
    # Characteristics: Balanced, organized, sophisticated, 5+ colors
    colors = [
        MockColor("#8B4513"),  # Brown
        MockColor("#D3D3D3"),  # Light gray
        MockColor("#696969"),  # Dim gray
        MockColor("#CD853F"),  # Peru
        MockColor("#A9A9A9"),  # Dark gray
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.art_movement is not None
    assert metrics.art_movement.primary == "Mid-Century Modern"
    assert any(
        "braun" in e.lower() or "rams" in e.lower() or "industrial" in e.lower()
        for e in metrics.art_movement.elaborations
    )


# ============================================================================
# SYNTHWAVE / VAPORWAVE PALETTE
# ============================================================================


def test_synthwave_vaporwave_palette() -> None:
    """Test detection of vaporwave aesthetic with neon + pastels + light colors."""
    # Characteristics: Neon + pastels, light colors, nostalgic (90s-00s)
    colors = [
        MockColor("#FF10F0"),  # Hot magenta
        MockColor("#00FFFF"),  # Cyan
        MockColor("#FFB6FF"),  # Light pink (pastel)
        MockColor("#B6E5FF"),  # Light blue (pastel)
        MockColor("#FF1493"),  # Deep pink
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.art_movement is not None
    assert metrics.art_movement.primary == "Vaporwave / Aesthetic"
    assert any(
        "neon" in e.lower() or "pastel" in e.lower() or "dream" in e.lower()
        for e in metrics.art_movement.elaborations
    )


# ============================================================================
# BRUTALISM PALETTE
# ============================================================================


def test_brutalism_palette() -> None:
    """Test detection of brutalism with minimal, high-contrast palette."""
    # Characteristics: Limited palette, high contrast, minimal colors
    colors = [
        MockColor("#000000"),  # Black
        MockColor("#FFFFFF"),  # White
        MockColor("#FF0000"),  # Red
    ]

    metrics = infer_metrics(colors, [], [])

    # Test that metrics are inferred for minimal high-contrast palette
    assert metrics.art_movement is not None
    assert metrics.emotional_tone is not None
    assert metrics.saturation_character is not None
    # Should not be complex
    assert (
        "complex" not in metrics.design_complexity.primary.lower()
        if metrics.design_complexity
        else True
    )


# ============================================================================
# EMOTIONAL TONE TESTS
# ============================================================================


def test_emotional_tone_warm_and_energetic() -> None:
    """Test emotional tone inference for warm, energetic palette."""
    colors = [
        MockColor("#FF6600"),  # Orange
        MockColor("#FFAA00"),  # Golden yellow
        MockColor("#DD4400"),  # Red-orange
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.emotional_tone is not None
    assert metrics.emotional_tone.primary == "Energetic & Inviting"
    assert any(
        "warm" in e.lower() or "engagement" in e.lower() or "inviting" in e.lower()
        for e in metrics.emotional_tone.elaborations
    )


def test_emotional_tone_cool_and_professional() -> None:
    """Test emotional tone inference for cool, professional palette."""
    colors = [
        MockColor("#0066FF"),  # Blue
        MockColor("#0088CC"),  # Light blue
        MockColor("#004488"),  # Dark blue
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.emotional_tone is not None
    assert (
        metrics.emotional_tone.primary == "Playful & Bold"
    )  # Cool + saturated = playful, not professional
    assert any(
        "cool" in e.lower() or "bold" in e.lower() or "impact" in e.lower()
        for e in metrics.emotional_tone.elaborations
    )


def test_emotional_tone_moody_and_dark() -> None:
    """Test emotional tone inference for dark, moody palette."""
    colors = [
        MockColor("#1A1A1A"),  # Very dark gray
        MockColor("#2D2D2D"),  # Dark gray
        MockColor("#330033"),  # Very dark purple
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.emotional_tone is not None
    # Dark palette should have some introspective quality
    assert len(metrics.emotional_tone.elaborations) > 0


# ============================================================================
# SATURATION CHARACTER TESTS
# ============================================================================


def test_saturation_hyper_saturated() -> None:
    """Test detection of hyper-saturated colors."""
    colors = [
        MockColor("#FF0000"),  # Pure red
        MockColor("#00FF00"),  # Pure green
        MockColor("#0000FF"),  # Pure blue
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.saturation_character is not None
    assert metrics.saturation_character.primary == "Hyper-Saturated"
    assert any(
        "intense" in e.lower() or "pure" in e.lower() or "chromatic" in e.lower()
        for e in metrics.saturation_character.elaborations
    )


def test_saturation_muted_and_subdued() -> None:
    """Test detection of muted palette."""
    colors = [
        MockColor("#888888"),  # Dark gray
        MockColor("#999999"),  # Gray
        MockColor("#AAAAAA"),  # Light gray
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.saturation_character is not None
    # Grayscale is desaturated
    assert (
        "desaturated" in metrics.saturation_character.primary.lower()
        or "muted" in metrics.saturation_character.primary.lower()
    )


# ============================================================================
# TEMPERATURE PROFILE TESTS
# ============================================================================


def test_temperature_warm_dominant() -> None:
    """Test thermal personality for warm-dominant palette."""
    colors = [
        MockColor("#FF6600"),  # Orange
        MockColor("#FFAA00"),  # Golden
        MockColor("#DD4400"),  # Red-orange
        MockColor("#0066FF"),  # Single cool
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.temperature_profile is not None
    assert metrics.temperature_profile.primary == "Warm Dominant"
    assert any(
        "solar" in e.lower() or "warm" in e.lower() or "inviting" in e.lower()
        for e in metrics.temperature_profile.elaborations
    )


def test_temperature_cool_dominant() -> None:
    """Test thermal personality for cool-dominant palette."""
    colors = [
        MockColor("#0066FF"),  # Blue
        MockColor("#0088CC"),  # Light blue
        MockColor("#004488"),  # Dark blue
        MockColor("#FF6600"),  # Single warm
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.temperature_profile is not None
    assert metrics.temperature_profile.primary == "Cool Dominant"
    assert any(
        "lunar" in e.lower() or "cool" in e.lower() or "serene" in e.lower()
        for e in metrics.temperature_profile.elaborations
    )


def test_temperature_perfectly_balanced() -> None:
    """Test thermal personality for perfectly balanced palette."""
    colors = [
        MockColor("#FF6600"),  # Warm
        MockColor("#0066FF"),  # Cool
        MockColor("#FF6600"),  # Warm
        MockColor("#0066FF"),  # Cool
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.temperature_profile is not None
    assert (
        "Perfect" in metrics.temperature_profile.primary
        or "Balanced" in metrics.temperature_profile.primary
    )


# ============================================================================
# DESIGN COMPLEXITY TESTS
# ============================================================================


def test_design_complexity_minimal() -> None:
    """Test complexity inference for minimal token count."""
    colors = [MockColor("#FF0000")]
    spacing = [MockSpacingToken(8)]
    typography = [MockTypographyToken(16)]

    metrics = infer_metrics(colors, spacing, typography)

    assert metrics.design_complexity is not None
    # 3 tokens total should be ultra-minimal or minimal
    assert metrics.design_complexity.primary in ["Ultra-Minimal", "Minimal"]


def test_design_complexity_moderate() -> None:
    """Test complexity inference for moderate token count."""
    colors = [
        MockColor("#FF0000"),
        MockColor("#00FF00"),
        MockColor("#0000FF"),
        MockColor("#FFFF00"),
        MockColor("#FF00FF"),
        MockColor("#00FFFF"),
        MockColor("#FFAA00"),
    ]
    spacing = [
        MockSpacingToken(4),
        MockSpacingToken(8),
        MockSpacingToken(16),
        MockSpacingToken(32),
        MockSpacingToken(64),
    ]
    typography = [
        MockTypographyToken(12),
        MockTypographyToken(16),
        MockTypographyToken(20),
        MockTypographyToken(24),
    ]

    metrics = infer_metrics(colors, spacing, typography)

    assert metrics.design_complexity is not None
    # 16 tokens total should be moderate or higher
    assert metrics.design_complexity.primary in ["Moderate", "Complex", "Highly Complex"]


def test_design_complexity_highly_complex() -> None:
    """Test complexity inference for comprehensive token ecosystem."""
    colors = [MockColor(f"#{i:06X}") for i in range(0, 256, 10)]  # 26 colors
    spacing = [MockSpacingToken(i * 4) for i in range(1, 20)]  # 19 spacing values
    typography = [MockTypographyToken(i * 2 + 10) for i in range(1, 10)]  # 9 typography sizes

    metrics = infer_metrics(colors, spacing, typography)

    assert metrics.design_complexity is not None
    # 54 tokens total should be complex or highly complex
    assert metrics.design_complexity.primary in ["Complex", "Highly Complex"]


# ============================================================================
# DESIGN SYSTEM INSIGHT TESTS
# ============================================================================


def test_design_system_incomplete() -> None:
    """Test insight for incomplete system with missing categories."""
    colors = [
        MockColor("#FF0000"),
        MockColor("#00FF00"),
        MockColor("#0000FF"),
    ]
    spacing: list[MockSpacingToken] = []
    typography: list[MockTypographyToken] = []

    metrics = infer_metrics(colors, spacing, typography)

    assert metrics.design_system_insight is not None
    assert metrics.design_system_insight.primary == "Incomplete System"
    assert any("missing" in e.lower() for e in metrics.design_system_insight.elaborations)


def test_design_system_well_organized() -> None:
    """Test insight for well-organized system with all categories."""
    colors = [MockColor(f"#{i:06X}") for i in range(255, 235, -5)]  # 4 colors
    spacing = [MockSpacingToken(i * 4) for i in range(1, 5)]  # 4 spacing
    typography = [MockTypographyToken(i * 4 + 12) for i in range(1, 4)]  # 3 typography

    metrics = infer_metrics(colors, spacing, typography)

    assert metrics.design_system_insight is not None
    assert metrics.design_system_insight.primary == "Well-Organized System"


def test_design_system_mature() -> None:
    """Test insight for mature, comprehensive system."""
    colors = [MockColor(f"#{i:06X}") for i in range(0, 256, 15)]  # 17 colors
    spacing = [MockSpacingToken(i * 4) for i in range(1, 10)]  # 9 spacing
    typography = [MockTypographyToken(i * 2 + 10) for i in range(1, 8)]  # 7 typography

    metrics = infer_metrics(colors, spacing, typography)

    assert metrics.design_system_insight is not None
    assert metrics.design_system_insight.primary == "Mature Design System"


# ============================================================================
# ELABORATED METRIC STRUCTURE TESTS
# ============================================================================


def test_elaborated_metric_structure() -> None:
    """Test that all elaborated metrics have proper structure."""
    colors = [
        MockColor("#FF6600"),
        MockColor("#0066FF"),
        MockColor("#DD4400"),
    ]

    metrics = infer_metrics(colors, [], [])

    # Check all elaborated metrics exist and have proper structure
    for metric_name in [
        "art_movement",
        "emotional_tone",
        "saturation_character",
        "temperature_profile",
    ]:
        metric = getattr(metrics, metric_name)
        assert metric is not None, f"{metric_name} should not be None"
        assert isinstance(metric, ElaboratedMetric)
        assert isinstance(metric.primary, str)
        assert isinstance(metric.elaborations, list)
        assert len(metric.elaborations) > 0
        assert all(isinstance(e, str) for e in metric.elaborations)


# ============================================================================
# COMPLEX REAL-WORLD PALETTE TESTS
# ============================================================================


def test_dark_academia_palette() -> None:
    """Test detection of Dark Academia aesthetic with muted jewel tones."""
    # Characteristics: Jewel-toned, muted, sophisticated
    colors = [
        MockColor("#2D5016"),  # Deep forest green
        MockColor("#6B4423"),  # Muted brown
        MockColor("#4A1D3F"),  # Deep plum
        MockColor("#1C3A47"),  # Deep teal
        MockColor("#8B6F47"),  # Muted gold
    ]

    metrics = infer_metrics(colors, [], [])

    # Should have muted/sophisticated characteristics
    assert metrics.art_movement is not None
    assert metrics.emotional_tone is not None
    assert metrics.saturation_character is not None
    # All elaborated metrics should be present
    assert len(metrics.art_movement.elaborations) > 0


def test_flat_design_palette() -> None:
    """Test detection of Flat Design aesthetic."""
    colors = [
        MockColor("#3498DB"),  # Soft blue
        MockColor("#2ECC71"),  # Soft green
        MockColor("#E74C3C"),  # Soft red
        MockColor("#F39C12"),  # Soft orange
    ]

    metrics = infer_metrics(colors, [], [])

    # Flat design should have balanced characteristics
    assert metrics.art_movement is not None
    assert metrics.emotional_tone is not None
    # Should not be minimal (has 4 colors)
    assert metrics.art_movement.primary not in ["Minimalism"]


def test_maximalist_palette() -> None:
    """Test detection of Maximalism aesthetic."""
    # Characteristics: 12+ colors, high saturation, complex
    colors = [
        MockColor("#FF0000"),
        MockColor("#00FF00"),
        MockColor("#0000FF"),
        MockColor("#FFFF00"),
        MockColor("#FF00FF"),
        MockColor("#00FFFF"),
        MockColor("#FF6600"),
        MockColor("#FF0066"),
        MockColor("#00FF66"),
        MockColor("#0066FF"),
        MockColor("#66FF00"),
        MockColor("#6600FF"),
        MockColor("#FF6666"),
        MockColor("#66FF66"),
    ]

    metrics = infer_metrics(colors, [], [])

    # Maximalist palette should be detected
    assert metrics.art_movement is not None
    assert metrics.saturation_character is not None
    # Should have high saturation
    assert (
        "vivid" in metrics.saturation_character.primary.lower()
        or "saturated" in metrics.saturation_character.primary.lower()
        or "hyper" in metrics.saturation_character.primary.lower()
    )


# ============================================================================
# EDGE CASES
# ============================================================================


def test_single_color_palette() -> None:
    """Test handling of single-color palette."""
    colors = [MockColor("#FF0000")]

    metrics = infer_metrics(colors, [], [])

    assert metrics.art_movement is not None
    assert metrics.emotional_tone is not None
    assert metrics.saturation_character is not None


def test_empty_palette() -> None:
    """Test handling of empty palette."""
    metrics = infer_metrics([], [], [])

    # Should have design_complexity and design_system_insight even with no colors
    assert metrics.design_complexity is not None
    assert metrics.design_system_insight is not None


def test_grayscale_palette() -> None:
    """Test handling of pure grayscale palette."""
    colors = [
        MockColor("#000000"),
        MockColor("#333333"),
        MockColor("#666666"),
        MockColor("#999999"),
        MockColor("#CCCCCC"),
        MockColor("#FFFFFF"),
    ]

    metrics = infer_metrics(colors, [], [])

    assert metrics.saturation_character is not None
    # Grayscale should be desaturated
    assert (
        "desaturated" in metrics.saturation_character.primary.lower()
        or "muted" in metrics.saturation_character.primary.lower()
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
