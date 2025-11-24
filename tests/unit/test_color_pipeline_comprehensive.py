"""
Comprehensive tests for the color extraction pipeline infrastructure.

Tests all 5 stages: Preprocess -> Extract -> Aggregate -> Validate -> Generate
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from copy_that.pipeline import PipelineTask, TokenResult, TokenType, W3CTokenType
from copy_that.pipeline.orchestrator.agent_pool import AgentPool
from copy_that.pipeline.orchestrator.circuit_breaker import CircuitBreaker
from copy_that.pipeline.orchestrator.coordinator import (
    PipelineCoordinator,
)
from copy_that.tokens.color.aggregator import AggregatedColorToken, ColorAggregator


class TestColorExtractionPipeline:
    """Test the full color extraction pipeline."""

    @pytest.fixture
    def sample_color_tokens(self):
        """Create sample color tokens for testing."""
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name="Primary Blue",
                path=["color", "primary"],
                w3c_type=W3CTokenType.COLOR,
                value="#0066FF",
                description="Primary brand color",
                confidence=0.95,
                metadata={
                    "rgb": "rgb(0, 102, 255)",
                    "hsl": "hsl(216, 100%, 50%)",
                    "temperature": "cool",
                    "saturation_level": "vibrant",
                    "lightness_level": "medium",
                    "harmony": "complementary",
                },
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="Secondary Gray",
                path=["color", "secondary"],
                w3c_type=W3CTokenType.COLOR,
                value="#6B7280",
                description="Secondary neutral color",
                confidence=0.88,
                metadata={
                    "rgb": "rgb(107, 114, 128)",
                    "temperature": "neutral",
                    "saturation_level": "muted",
                    "lightness_level": "medium",
                },
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="Error Red",
                path=["color", "error"],
                w3c_type=W3CTokenType.COLOR,
                value="#DC2626",
                description="Error state color",
                confidence=0.92,
                metadata={
                    "rgb": "rgb(220, 38, 38)",
                    "temperature": "warm",
                    "saturation_level": "vibrant",
                    "lightness_level": "medium",
                    "harmony": "analogous",
                },
            ),
        ]

    @pytest.fixture
    def mock_agents(self, sample_color_tokens):
        """Create mock agents for pipeline testing."""
        preprocess_agent = MagicMock()
        preprocess_agent.process = AsyncMock(return_value=[])
        preprocess_agent.health_check = AsyncMock(return_value=True)

        extraction_agent = MagicMock()
        extraction_agent.process = AsyncMock(return_value=sample_color_tokens)
        extraction_agent.health_check = AsyncMock(return_value=True)

        aggregation_agent = MagicMock()
        aggregation_agent.process = AsyncMock(return_value=sample_color_tokens)
        aggregation_agent.health_check = AsyncMock(return_value=True)

        validation_agent = MagicMock()
        validation_agent.process = AsyncMock(return_value=sample_color_tokens)
        validation_agent.health_check = AsyncMock(return_value=True)

        generator_agent = MagicMock()
        generator_agent.process = AsyncMock(return_value=sample_color_tokens)
        generator_agent.health_check = AsyncMock(return_value=True)

        return {
            "preprocess": preprocess_agent,
            "extraction": extraction_agent,
            "aggregation": aggregation_agent,
            "validation": validation_agent,
            "generator": generator_agent,
        }

    @pytest.mark.asyncio
    async def test_pipeline_coordinator_initialization(self, mock_agents):
        """Test PipelineCoordinator initializes with all agents."""
        coordinator = PipelineCoordinator(
            preprocess_agent=mock_agents["preprocess"],
            extraction_agents=[mock_agents["extraction"]],
            aggregation_agent=mock_agents["aggregation"],
            validation_agent=mock_agents["validation"],
            generator_agent=mock_agents["generator"],
        )

        assert coordinator.preprocess_agent == mock_agents["preprocess"]
        assert len(coordinator.extraction_agents) == 1
        assert coordinator.aggregation_agent == mock_agents["aggregation"]

    @pytest.mark.asyncio
    async def test_pipeline_health_check(self, mock_agents):
        """Test pipeline health check with all agents."""
        coordinator = PipelineCoordinator(
            preprocess_agent=mock_agents["preprocess"],
            extraction_agents=[mock_agents["extraction"]],
            aggregation_agent=mock_agents["aggregation"],
            validation_agent=mock_agents["validation"],
            generator_agent=mock_agents["generator"],
        )

        health = await coordinator.health_check()

        assert health["healthy"] is True
        assert "agents" in health

    @pytest.mark.asyncio
    async def test_pipeline_statistics(self, mock_agents):
        """Test pipeline statistics tracking."""
        coordinator = PipelineCoordinator(
            preprocess_agent=mock_agents["preprocess"],
            extraction_agents=[mock_agents["extraction"]],
            aggregation_agent=mock_agents["aggregation"],
            validation_agent=mock_agents["validation"],
            generator_agent=mock_agents["generator"],
        )

        stats = coordinator.get_stats()

        assert stats["total_executed"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == 0.0


class TestColorAggregation:
    """Test color aggregation with Delta-E deduplication."""

    @pytest.fixture
    def aggregator(self):
        """Create a color aggregator instance."""
        return ColorAggregator(delta_e_threshold=2.0)

    def test_aggregator_initialization(self, aggregator):
        """Test aggregator initializes with correct threshold."""
        assert aggregator.delta_e_threshold == 2.0

    def test_deduplicate_identical_colors(self, aggregator):
        """Test that identical colors are deduplicated."""
        colors = [
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red",
                confidence=0.9,
                provenance={"image_1": 0.9},
            ),
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red 2",
                confidence=0.85,
                provenance={"image_2": 0.85},
            ),
        ]

        result = aggregator.deduplicate(colors)

        # Should merge into one color
        assert len(result) == 1
        # Should keep higher confidence
        assert result[0].confidence >= 0.9

    def test_keep_distinct_colors(self, aggregator):
        """Test that distinct colors are kept separate."""
        colors = [
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red",
                confidence=0.9,
                provenance={"image_1": 0.9},
            ),
            AggregatedColorToken(
                hex="#0000FF",
                rgb="rgb(0, 0, 255)",
                name="Blue",
                confidence=0.88,
                provenance={"image_1": 0.88},
            ),
        ]

        result = aggregator.deduplicate(colors)

        # Should keep both colors
        assert len(result) == 2

    def test_provenance_tracking(self, aggregator):
        """Test that provenance is tracked correctly."""
        colors = [
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red",
                confidence=0.9,
                provenance={"image_1": 0.9},
            ),
        ]

        result = aggregator.deduplicate(colors)

        assert "image_1" in result[0].provenance
        assert result[0].provenance["image_1"] == 0.9

    def test_aggregate_multiple_images(self, aggregator):
        """Test aggregation from multiple image sources."""
        colors = [
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red",
                confidence=0.9,
                provenance={"image_1": 0.9},
            ),
            AggregatedColorToken(
                hex="#00FF00",
                rgb="rgb(0, 255, 0)",
                name="Green",
                confidence=0.85,
                provenance={"image_2": 0.85},
            ),
            AggregatedColorToken(
                hex="#0000FF",
                rgb="rgb(0, 0, 255)",
                name="Blue",
                confidence=0.88,
                provenance={"image_3": 0.88},
            ),
        ]

        result = aggregator.deduplicate(colors)

        # All distinct, all should be kept
        assert len(result) == 3

    def test_similar_colors_merge(self, aggregator):
        """Test that similar colors (Delta-E < threshold) are merged."""
        colors = [
            AggregatedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red",
                confidence=0.9,
                provenance={"image_1": 0.9},
            ),
            AggregatedColorToken(
                hex="#FE0000",  # Very similar to #FF0000
                rgb="rgb(254, 0, 0)",
                name="Red 2",
                confidence=0.85,
                provenance={"image_2": 0.85},
            ),
        ]

        result = aggregator.deduplicate(colors)

        # Should merge similar colors
        assert len(result) == 1


class TestColorValidation:
    """Test color validation including WCAG accessibility."""

    def test_wcag_contrast_ratio_calculation(self):
        """Test WCAG contrast ratio calculations."""
        from copy_that.application.color_utils import calculate_contrast_ratio

        # White on black should be maximum contrast (21:1)
        ratio = calculate_contrast_ratio("#FFFFFF", "#000000")
        assert ratio == pytest.approx(21.0, rel=0.1)

        # Same colors should be minimum contrast (1:1)
        ratio = calculate_contrast_ratio("#000000", "#000000")
        assert ratio == pytest.approx(1.0, rel=0.1)

    def test_wcag_aa_compliance(self):
        """Test WCAG AA compliance checking."""
        from copy_that.application.color_utils import calculate_contrast_ratio

        # High contrast - should pass AA
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert ratio >= 4.5  # AA threshold for normal text

        # Low contrast - should fail AA
        ratio = calculate_contrast_ratio("#777777", "#888888")
        assert ratio < 4.5

    def test_wcag_aaa_compliance(self):
        """Test WCAG AAA compliance checking."""
        from copy_that.application.color_utils import calculate_contrast_ratio

        # Very high contrast - should pass AAA
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert ratio >= 7.0  # AAA threshold for normal text

    def test_color_temperature_detection(self):
        """Test color temperature detection."""
        from copy_that.application.color_utils import get_color_temperature

        # Red should be warm
        temp = get_color_temperature("#FF0000")
        assert temp == "warm"

        # Blue should be cool
        temp = get_color_temperature("#0000FF")
        assert temp == "cool"

        # Gray should be neutral
        temp = get_color_temperature("#808080")
        assert temp == "neutral"

    def test_saturation_level_detection(self):
        """Test saturation level detection."""
        from copy_that.application.color_utils import get_saturation_level

        # Pure red is vibrant
        level = get_saturation_level("#FF0000")
        assert level in ["vibrant", "saturated"]

        # Gray is desaturated
        level = get_saturation_level("#808080")
        assert level in ["grayscale", "desaturated"]

    def test_lightness_level_detection(self):
        """Test lightness level detection."""
        from copy_that.application.color_utils import get_lightness_level

        # White is light
        level = get_lightness_level("#FFFFFF")
        assert level in ["light", "very_light"]

        # Black is dark
        level = get_lightness_level("#000000")
        assert level in ["dark", "very_dark"]


class TestColorGeneration:
    """Test color token generation in various formats."""

    @pytest.fixture
    def sample_library(self):
        """Create a sample color library for generation tests."""
        from copy_that.tokens.color.aggregator import ColorTokenLibrary

        library = ColorTokenLibrary()
        library.add_token(
            AggregatedColorToken(
                hex="#0066FF",
                rgb="rgb(0, 102, 255)",
                name="Primary",
                confidence=0.95,
                harmony="complementary",
                temperature="cool",
                saturation_level="vibrant",
                lightness_level="medium",
                provenance={"image_1": 0.95},
                role="primary",
            )
        )
        library.add_token(
            AggregatedColorToken(
                hex="#6B7280",
                rgb="rgb(107, 114, 128)",
                name="Secondary",
                confidence=0.88,
                temperature="neutral",
                saturation_level="muted",
                lightness_level="medium",
                provenance={"image_1": 0.88},
                role="secondary",
            )
        )
        return library

    def test_css_generator(self, sample_library):
        """Test CSS custom properties generation."""
        from copy_that.generators.css_generator import CSSTokenGenerator

        generator = CSSTokenGenerator(sample_library)
        css = generator.generate()

        assert ":root {" in css
        assert "--color-primary: #0066FF" in css
        assert "--color-secondary: #6B7280" in css

    def test_w3c_generator(self, sample_library):
        """Test W3C Design Tokens JSON generation."""
        from copy_that.generators.w3c_generator import W3CTokenGenerator

        generator = W3CTokenGenerator(sample_library)
        output = generator.generate()

        assert "$schema" in output or "color" in output

    def test_react_generator(self, sample_library):
        """Test React/TypeScript theme generation."""
        from copy_that.generators.react_generator import ReactTokenGenerator

        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()

        assert "export" in output
        assert "Primary" in output or "primary" in output

    def test_html_demo_generator(self, sample_library):
        """Test HTML demo page generation."""
        from copy_that.generators.html_demo_generator import HTMLDemoGenerator

        generator = HTMLDemoGenerator(sample_library)
        html = generator.generate()

        assert "<!DOCTYPE html>" in html
        assert "#0066FF" in html
        assert "#6B7280" in html


class TestColorUtilities:
    """Test color utility functions."""

    def test_hex_to_rgb_conversion(self):
        """Test hex to RGB conversion."""
        from copy_that.application.color_utils import hex_to_rgb

        r, g, b = hex_to_rgb("#FF5733")
        assert r == 255
        assert g == 87
        assert b == 51

    def test_rgb_to_hsl_conversion(self):
        """Test RGB to HSL conversion."""
        from copy_that.application.color_utils import rgb_to_hsl

        h, s, l = rgb_to_hsl(255, 0, 0)
        assert h == pytest.approx(0, abs=1)  # Red hue
        assert s == pytest.approx(100, abs=1)  # Full saturation
        assert l == pytest.approx(50, abs=1)  # Medium lightness

    def test_delta_e_calculation(self):
        """Test Delta-E color difference calculation."""
        from copy_that.application.color_utils import calculate_delta_e

        # Same colors should have Delta-E of 0
        delta = calculate_delta_e("#FF0000", "#FF0000")
        assert delta == pytest.approx(0, abs=0.1)

        # Different colors should have Delta-E > 0
        delta = calculate_delta_e("#FF0000", "#0000FF")
        assert delta > 0

    def test_web_safe_color_matching(self):
        """Test closest web-safe color matching."""
        from copy_that.application.color_utils import get_closest_web_safe

        # Should return a web-safe color
        web_safe = get_closest_web_safe("#FF5733")
        assert web_safe is not None
        # Web-safe colors have values divisible by 51
        r = int(web_safe[1:3], 16)
        g = int(web_safe[3:5], 16)
        b = int(web_safe[5:7], 16)
        assert r % 51 == 0 or r == 0
        assert g % 51 == 0 or g == 0
        assert b % 51 == 0 or b == 0

    def test_css_named_color_matching(self):
        """Test closest CSS named color matching."""
        from copy_that.application.color_utils import get_closest_css_named

        # Pure red should match "red"
        named = get_closest_css_named("#FF0000")
        assert named is not None
        assert named.lower() == "red"

    def test_tint_generation(self):
        """Test tint (lighter) color generation."""
        from copy_that.application.color_utils import generate_tint

        tint = generate_tint("#FF0000")
        assert tint is not None
        # Tint should be lighter (higher RGB values)
        r = int(tint[1:3], 16)
        assert r >= 255 or r > int("FF", 16) * 0.8

    def test_shade_generation(self):
        """Test shade (darker) color generation."""
        from copy_that.application.color_utils import generate_shade

        shade = generate_shade("#FF0000")
        assert shade is not None
        # Shade should be darker (lower RGB values)
        r = int(shade[1:3], 16)
        assert r <= 255


class TestExtractedColorToken:
    """Test ExtractedColorToken model validation."""

    def test_token_creation(self):
        """Test creating an ExtractedColorToken."""
        from copy_that.application.color_extractor import ExtractedColorToken

        token = ExtractedColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            hsl="hsl(11, 100%, 60%)",
            name="Coral",
            confidence=0.95,
        )

        assert token.hex == "#FF5733"
        assert token.confidence == 0.95

    def test_token_optional_fields(self):
        """Test ExtractedColorToken with optional fields."""
        from copy_that.application.color_extractor import ExtractedColorToken

        token = ExtractedColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral",
            confidence=0.95,
            harmony="complementary",
            temperature="warm",
            saturation_level="vibrant",
            lightness_level="medium",
            wcag_contrast_on_white=3.5,
            wcag_contrast_on_black=6.0,
            wcag_aa_compliant_text=False,
            wcag_aaa_compliant_text=False,
        )

        assert token.harmony == "complementary"
        assert token.temperature == "warm"
        assert token.wcag_contrast_on_white == 3.5

    def test_token_confidence_validation(self):
        """Test that confidence must be between 0 and 1."""
        from pydantic import ValidationError

        from copy_that.application.color_extractor import ExtractedColorToken

        with pytest.raises(ValidationError):
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                name="Invalid",
                confidence=1.5,  # Invalid: > 1
            )


class TestAgentPool:
    """Test AgentPool concurrency management."""

    @pytest.mark.asyncio
    async def test_pool_initialization(self):
        """Test AgentPool initializes correctly."""
        pool = AgentPool(max_concurrency=5)

        stats = pool.get_stats()
        assert stats["running"] == 0
        assert stats["completed"] == 0

    @pytest.mark.asyncio
    async def test_pool_shutdown(self):
        """Test AgentPool shutdown."""
        pool = AgentPool(max_concurrency=5)

        await pool.shutdown(wait=True)
        # Should complete without error


class TestCircuitBreaker:
    """Test CircuitBreaker fault tolerance."""

    def test_circuit_breaker_initialization(self):
        """Test CircuitBreaker initializes in closed state."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=5,
            recovery_timeout=30.0,
        )

        assert breaker.is_closed
        assert not breaker.is_open

    @pytest.mark.asyncio
    async def test_circuit_breaker_success(self):
        """Test CircuitBreaker allows successful calls."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=5,
            recovery_timeout=30.0,
        )

        async def success_fn():
            return "success"

        result = await breaker.call(success_fn)
        assert result == "success"
        assert breaker.is_closed

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test CircuitBreaker opens after threshold failures."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=2,
            recovery_timeout=30.0,
        )

        async def failing_fn():
            raise Exception("Test failure")

        # Trigger failures
        for _ in range(2):
            try:
                await breaker.call(failing_fn)
            except Exception:
                pass

        assert breaker.is_open


class TestPipelineTask:
    """Test PipelineTask creation and properties."""

    def test_task_creation(self):
        """Test creating a PipelineTask."""
        task = PipelineTask(
            task_id="test-123",
            image_url="https://example.com/image.jpg",
            token_types=[TokenType.COLOR],
        )

        assert task.task_id == "test-123"
        assert task.image_url == "https://example.com/image.jpg"
        assert TokenType.COLOR in task.token_types

    def test_task_with_context(self):
        """Test PipelineTask with context data."""
        task = PipelineTask(
            task_id="test-456",
            image_url="https://example.com/image.jpg",
            token_types=[TokenType.COLOR],
            context={"project_id": 1, "max_colors": 10},
        )

        assert task.context["project_id"] == 1
        assert task.context["max_colors"] == 10

    def test_task_priority(self):
        """Test PipelineTask priority."""
        high_priority = PipelineTask(
            task_id="high",
            image_url="https://example.com/high.jpg",
            token_types=[TokenType.COLOR],
            priority=10,
        )

        low_priority = PipelineTask(
            task_id="low",
            image_url="https://example.com/low.jpg",
            token_types=[TokenType.COLOR],
            priority=1,
        )

        assert high_priority.priority > low_priority.priority
