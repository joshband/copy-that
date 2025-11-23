"""Tests for ExtractionAgent.

Tests written BEFORE implementation (TDD approach).
Uses mocked Anthropic client for unit testing.
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from copy_that.pipeline import (
    ExtractionError,
    PipelineTask,
    TokenResult,
    TokenType,
    W3CTokenType,
)
from copy_that.pipeline.extraction.agent import ExtractionAgent


# Shared mock image data fixture
@pytest.fixture
def mock_image_data():
    """Mock image data returned by _get_image_data."""
    return {
        "type": "base64",
        "media_type": "image/png",
        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    }


class TestExtractionAgentProperties:
    """Test ExtractionAgent properties and initialization."""

    def test_agent_type_property(self):
        """Agent type should be 'extraction_agent'."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)
        assert agent.agent_type == "extraction_agent"

    def test_stage_name_property(self):
        """Stage name should be 'extraction'."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)
        assert agent.stage_name == "extraction"

    def test_init_with_token_type(self):
        """Agent should initialize with token type configuration."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)
        assert agent.token_type == TokenType.COLOR

    def test_init_with_different_token_types(self):
        """Agent should support all token types."""
        for token_type in TokenType:
            agent = ExtractionAgent(token_type=token_type)
            assert agent.token_type == token_type

    def test_init_with_custom_timeout(self):
        """Agent should accept custom timeout configuration."""
        agent = ExtractionAgent(token_type=TokenType.COLOR, timeout=60.0)
        assert agent.timeout == 60.0

    def test_init_with_custom_max_retries(self):
        """Agent should accept custom max retries configuration."""
        agent = ExtractionAgent(token_type=TokenType.COLOR, max_retries=5)
        assert agent.max_retries == 5

    def test_init_with_api_key(self):
        """Agent should accept API key for Anthropic client."""
        agent = ExtractionAgent(token_type=TokenType.COLOR, api_key="test-key")
        assert agent._api_key == "test-key"


class TestExtractionAgentHealthCheck:
    """Test ExtractionAgent health check."""

    @pytest.mark.asyncio
    async def test_health_check_returns_true_when_healthy(self):
        """Health check should return True when client is available."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)
        # Mock the client
        agent._client = MagicMock()

        result = await agent.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_returns_false_when_no_client(self):
        """Health check should return False when client is None."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)
        agent._client = None

        result = await agent.health_check()
        assert result is False


class TestExtractionAgentProcess:
    """Test ExtractionAgent process method with mocked Anthropic client."""

    @pytest.fixture
    def mock_anthropic_response_color(self):
        """Mock Anthropic response for color extraction."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={
                    "colors": [
                        {
                            "name": "primary-blue",
                            "hex_value": "#0066CC",
                            "confidence": 0.95,
                            "rgb": {"r": 0, "g": 102, "b": 204},
                            "usage": "Primary brand color",
                            "category": "brand",
                        },
                        {
                            "name": "accent-orange",
                            "hex_value": "#FF6B35",
                            "confidence": 0.88,
                            "rgb": {"r": 255, "g": 107, "b": 53},
                            "usage": "Accent color for CTAs",
                            "category": "accent",
                        },
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"
        return mock_response

    @pytest.fixture
    def mock_anthropic_response_spacing(self):
        """Mock Anthropic response for spacing extraction."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_spacing",
                input={
                    "spacing": [
                        {
                            "name": "space-xs",
                            "value": 4,
                            "unit": "px",
                            "confidence": 0.90,
                            "scale_position": 1,
                        },
                        {
                            "name": "space-sm",
                            "value": 8,
                            "unit": "px",
                            "confidence": 0.92,
                            "scale_position": 2,
                        },
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"
        return mock_response

    @pytest.fixture
    def mock_anthropic_response_typography(self):
        """Mock Anthropic response for typography extraction."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_typography",
                input={
                    "typography": [
                        {
                            "name": "heading-1",
                            "font_family": "Inter",
                            "font_size": {"value": 32, "unit": "px"},
                            "font_weight": 700,
                            "line_height": {"value": 1.2, "unit": "em"},
                            "confidence": 0.93,
                        }
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"
        return mock_response

    @pytest.fixture
    def mock_anthropic_response_shadow(self):
        """Mock Anthropic response for shadow extraction."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_shadows",
                input={
                    "shadows": [
                        {
                            "name": "shadow-md",
                            "offset_x": {"value": 0, "unit": "px"},
                            "offset_y": {"value": 4, "unit": "px"},
                            "blur_radius": {"value": 6, "unit": "px"},
                            "spread_radius": {"value": -1, "unit": "px"},
                            "color": "rgba(0, 0, 0, 0.1)",
                            "confidence": 0.85,
                        }
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"
        return mock_response

    @pytest.fixture
    def mock_anthropic_response_gradient(self):
        """Mock Anthropic response for gradient extraction."""
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_gradients",
                input={
                    "gradients": [
                        {
                            "name": "gradient-primary",
                            "type": "linear",
                            "angle": 90,
                            "stops": [
                                {"color": "#FF6B35", "position": 0},
                                {"color": "#F7C59F", "position": 100},
                            ],
                            "confidence": 0.88,
                        }
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"
        return mock_response

    @pytest.mark.asyncio
    async def test_process_returns_token_results(
        self, mock_image_data, mock_anthropic_response_color
    ):
        """Process should return list of TokenResult objects."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_color),
        ):
            task = PipelineTask(
                task_id="test-1",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(r, TokenResult) for r in results)

    @pytest.mark.asyncio
    async def test_process_returns_correct_token_type(
        self, mock_image_data, mock_anthropic_response_color
    ):
        """Results should have correct token type."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_color),
        ):
            task = PipelineTask(
                task_id="test-1",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            assert all(r.token_type == TokenType.COLOR for r in results)

    @pytest.mark.asyncio
    async def test_process_returns_w3c_type(self, mock_image_data, mock_anthropic_response_color):
        """Results should have correct W3C type for colors."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_color),
        ):
            task = PipelineTask(
                task_id="test-1",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            # Color tokens should have W3C type COLOR
            assert all(r.w3c_type == W3CTokenType.COLOR for r in results)

    @pytest.mark.asyncio
    async def test_process_returns_confidence(self, mock_image_data, mock_anthropic_response_color):
        """Results should include confidence scores."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_color),
        ):
            task = PipelineTask(
                task_id="test-1",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            assert results[0].confidence == 0.95
            assert results[1].confidence == 0.88

    @pytest.mark.asyncio
    async def test_process_color_token_values(self, mock_image_data, mock_anthropic_response_color):
        """Color tokens should have correct hex values."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_color),
        ):
            task = PipelineTask(
                task_id="test-1",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            assert results[0].name == "primary-blue"
            assert results[0].value == "#0066CC"
            assert results[1].name == "accent-orange"
            assert results[1].value == "#FF6B35"

    @pytest.mark.asyncio
    async def test_process_spacing_tokens(self, mock_image_data, mock_anthropic_response_spacing):
        """Agent should extract spacing tokens correctly."""
        agent = ExtractionAgent(token_type=TokenType.SPACING)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_spacing),
        ):
            task = PipelineTask(
                task_id="test-2",
                image_url="https://example.com/image.png",
                token_types=[TokenType.SPACING],
            )

            results = await agent.process(task)

            assert len(results) == 2
            assert all(r.token_type == TokenType.SPACING for r in results)
            assert all(r.w3c_type == W3CTokenType.DIMENSION for r in results)
            assert results[0].name == "space-xs"
            # Value should be formatted as dimension string
            assert "4" in str(results[0].value)

    @pytest.mark.asyncio
    async def test_process_typography_tokens(
        self, mock_image_data, mock_anthropic_response_typography
    ):
        """Agent should extract typography tokens correctly."""
        agent = ExtractionAgent(token_type=TokenType.TYPOGRAPHY)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_typography),
        ):
            task = PipelineTask(
                task_id="test-3",
                image_url="https://example.com/image.png",
                token_types=[TokenType.TYPOGRAPHY],
            )

            results = await agent.process(task)

            assert len(results) == 1
            assert results[0].token_type == TokenType.TYPOGRAPHY
            assert results[0].w3c_type == W3CTokenType.TYPOGRAPHY
            assert results[0].name == "heading-1"

    @pytest.mark.asyncio
    async def test_process_shadow_tokens(self, mock_image_data, mock_anthropic_response_shadow):
        """Agent should extract shadow tokens correctly."""
        agent = ExtractionAgent(token_type=TokenType.SHADOW)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_shadow),
        ):
            task = PipelineTask(
                task_id="test-4",
                image_url="https://example.com/image.png",
                token_types=[TokenType.SHADOW],
            )

            results = await agent.process(task)

            assert len(results) == 1
            assert results[0].token_type == TokenType.SHADOW
            assert results[0].w3c_type == W3CTokenType.SHADOW
            assert results[0].name == "shadow-md"

    @pytest.mark.asyncio
    async def test_process_gradient_tokens(self, mock_image_data, mock_anthropic_response_gradient):
        """Agent should extract gradient tokens correctly."""
        agent = ExtractionAgent(token_type=TokenType.GRADIENT)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_anthropic_response_gradient),
        ):
            task = PipelineTask(
                task_id="test-5",
                image_url="https://example.com/image.png",
                token_types=[TokenType.GRADIENT],
            )

            results = await agent.process(task)

            assert len(results) == 1
            assert results[0].token_type == TokenType.GRADIENT
            assert results[0].w3c_type == W3CTokenType.GRADIENT
            assert results[0].name == "gradient-primary"


class TestExtractionAgentErrorHandling:
    """Test ExtractionAgent error handling, retries, and timeouts."""

    @pytest.mark.asyncio
    async def test_raises_extraction_error_on_api_failure(self, mock_image_data):
        """Agent should raise ExtractionError on API failure."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", side_effect=Exception("API Error")),
        ):
            task = PipelineTask(
                task_id="test-fail",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            with pytest.raises(ExtractionError) as exc_info:
                await agent.process(task)

            assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retries_on_rate_limit(self, mock_image_data):
        """Agent should retry on rate limit errors."""
        agent = ExtractionAgent(token_type=TokenType.COLOR, max_retries=3)

        # Mock rate limit error then success
        rate_limit_error = Exception("rate_limit_error")
        rate_limit_error.status_code = 429

        success_response = MagicMock()
        success_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={"colors": [{"name": "test", "hex_value": "#FF0000", "confidence": 0.9}]},
            )
        ]
        success_response.stop_reason = "tool_use"

        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise rate_limit_error
            return success_response

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", side_effect=mock_call),
        ):
            task = PipelineTask(
                task_id="test-retry",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            assert len(results) == 1
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_raises_extraction_error(self, mock_image_data):
        """Agent should raise ExtractionError on timeout."""
        agent = ExtractionAgent(token_type=TokenType.COLOR, timeout=0.001)

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        async def slow_call(*args, **kwargs):
            await asyncio.sleep(1)
            return MagicMock()

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", side_effect=slow_call),
        ):
            task = PipelineTask(
                task_id="test-timeout",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            with pytest.raises(ExtractionError) as exc_info:
                await agent.process(task)

            assert (
                "timeout" in str(exc_info.value).lower()
                or "timed out" in str(exc_info.value).lower()
            )

    @pytest.mark.asyncio
    async def test_invalid_response_raises_extraction_error(self, mock_image_data):
        """Agent should raise ExtractionError on invalid response."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        # Mock invalid response (no tool_use)
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Invalid")]
        mock_response.stop_reason = "end_turn"

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_response),
        ):
            task = PipelineTask(
                task_id="test-invalid",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            with pytest.raises(ExtractionError):
                await agent.process(task)


class TestExtractionAgentMetadata:
    """Test metadata handling in extraction results."""

    @pytest.mark.asyncio
    async def test_results_include_metadata(self, mock_image_data):
        """Results should include extraction metadata."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={
                    "colors": [
                        {
                            "name": "primary",
                            "hex_value": "#0066CC",
                            "confidence": 0.95,
                            "rgb": {"r": 0, "g": 102, "b": 204},
                            "usage": "Brand color",
                            "category": "brand",
                        }
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_response),
        ):
            task = PipelineTask(
                task_id="test-meta",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            # Check metadata is populated
            assert results[0].metadata is not None
            assert "rgb" in results[0].metadata

    @pytest.mark.asyncio
    async def test_results_include_description(self, mock_image_data):
        """Results should include usage as description."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={
                    "colors": [
                        {
                            "name": "primary",
                            "hex_value": "#0066CC",
                            "confidence": 0.95,
                            "usage": "Primary brand color",
                        }
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_response),
        ):
            task = PipelineTask(
                task_id="test-desc",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            assert results[0].description == "Primary brand color"


class TestExtractionAgentImageHandling:
    """Test image handling in extraction process."""

    @pytest.mark.asyncio
    async def test_process_uses_image_url(self, mock_image_data):
        """Agent should use image URL from task."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={"colors": [{"name": "test", "hex_value": "#FF0000", "confidence": 0.9}]},
            )
        ]
        mock_response.stop_reason = "tool_use"

        captured_image_data = {}

        async def mock_get_image(task):
            captured_image_data["url"] = task.image_url
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_response),
        ):
            task = PipelineTask(
                task_id="test-url",
                image_url="https://example.com/specific-image.png",
                token_types=[TokenType.COLOR],
            )

            await agent.process(task)

            # Verify the image URL was used
            assert captured_image_data["url"] == "https://example.com/specific-image.png"

    @pytest.mark.asyncio
    async def test_process_handles_preprocessed_image(self):
        """Agent should handle preprocessed image data if available."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={"colors": [{"name": "test", "hex_value": "#FF0000", "confidence": 0.9}]},
            )
        ]
        mock_response.stop_reason = "tool_use"

        with patch.object(agent, "_call_anthropic", return_value=mock_response):
            from copy_that.pipeline import ProcessedImage

            preprocessed = ProcessedImage(
                image_id="preprocessed-1",
                source_url="https://example.com/image.png",
                width=800,
                height=600,
                format="png",
                preprocessed_data={"base64": "abc123=="},
            )

            task = PipelineTask(
                task_id="test-preprocessed",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
                context={"preprocessed_image": preprocessed},
            )

            results = await agent.process(task)
            assert len(results) >= 1


class TestExtractionAgentW3CCompliance:
    """Test W3C Design Tokens compliance of results."""

    @pytest.mark.asyncio
    async def test_results_can_convert_to_w3c(self, mock_image_data):
        """Results should be convertible to W3C format."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={
                    "colors": [
                        {
                            "name": "primary",
                            "hex_value": "#0066CC",
                            "confidence": 0.95,
                            "usage": "Brand color",
                        }
                    ]
                },
            )
        ]
        mock_response.stop_reason = "tool_use"

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_response),
        ):
            task = PipelineTask(
                task_id="test-w3c",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            # Convert to W3C format
            w3c_dict = results[0].to_w3c_dict()

            assert "$value" in w3c_dict
            assert w3c_dict["$value"] == "#0066CC"
            assert "$type" in w3c_dict
            assert w3c_dict["$type"] == "color"

    @pytest.mark.asyncio
    async def test_results_have_full_path(self, mock_image_data):
        """Results should have properly formatted full path."""
        agent = ExtractionAgent(token_type=TokenType.COLOR)

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="tool_use",
                name="extract_colors",
                input={"colors": [{"name": "primary", "hex_value": "#0066CC", "confidence": 0.95}]},
            )
        ]
        mock_response.stop_reason = "tool_use"

        async def mock_get_image(*args, **kwargs):
            return mock_image_data

        with (
            patch.object(agent, "_get_image_data", side_effect=mock_get_image),
            patch.object(agent, "_call_anthropic", return_value=mock_response),
        ):
            task = PipelineTask(
                task_id="test-path",
                image_url="https://example.com/image.png",
                token_types=[TokenType.COLOR],
            )

            results = await agent.process(task)

            # Check path is set
            assert results[0].path is not None
            # Check full_path property works
            full_path = results[0].full_path
            assert "primary" in full_path
