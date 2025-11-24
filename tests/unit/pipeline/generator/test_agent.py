"""
Tests for GeneratorAgent.

Tests the core GeneratorAgent functionality including:
- Initialization with different formats
- Processing tasks with token results
- Health checks
- Error handling
"""

import pytest

from copy_that.pipeline import (
    GenerationError,
    PipelineTask,
    TokenResult,
    TokenType,
    W3CTokenType,
)
from copy_that.pipeline.generator import GeneratorAgent, OutputFormat


@pytest.fixture
def sample_tokens():
    """Shared sample tokens for generator tests."""
    return [
        TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            path=["color", "brand"],
            w3c_type=W3CTokenType.COLOR,
            value="#FF6B35",
            confidence=0.95,
            description="Primary brand color",
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="secondary",
            path=["color", "brand"],
            w3c_type=W3CTokenType.COLOR,
            value="#004E89",
            confidence=0.90,
            description="Secondary brand color",
        ),
        TokenResult(
            token_type=TokenType.SPACING,
            name="small",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="8px",
            confidence=0.88,
            description="Small spacing unit",
        ),
    ]


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_all_formats_defined(self):
        """All expected formats are defined."""
        expected = {"w3c", "css", "scss", "react", "tailwind", "figma"}
        actual = {fmt.value for fmt in OutputFormat}
        assert actual == expected

    def test_format_values_are_strings(self):
        """All format values are strings."""
        for fmt in OutputFormat:
            assert isinstance(fmt.value, str)


class TestGeneratorAgentInit:
    """Tests for GeneratorAgent initialization."""

    def test_default_format_is_w3c(self):
        """Default format should be W3C."""
        agent = GeneratorAgent()
        assert agent.output_format == OutputFormat.W3C

    def test_init_with_specific_format(self):
        """Agent initializes with specified format."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        assert agent.output_format == OutputFormat.CSS

    def test_init_with_all_formats(self):
        """Agent can be initialized with all supported formats."""
        for fmt in OutputFormat:
            agent = GeneratorAgent(output_format=fmt)
            assert agent.output_format == fmt

    def test_init_with_string_format(self):
        """Agent can be initialized with string format."""
        agent = GeneratorAgent(output_format="css")
        assert agent.output_format == OutputFormat.CSS

    def test_init_with_invalid_string_format_raises(self):
        """Invalid string format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid output format"):
            GeneratorAgent(output_format="invalid")


class TestGeneratorAgentProperties:
    """Tests for GeneratorAgent properties."""

    def test_agent_type(self):
        """Agent type is 'generator'."""
        agent = GeneratorAgent()
        assert agent.agent_type == "generator"

    def test_stage_name(self):
        """Stage name is 'generation'."""
        agent = GeneratorAgent()
        assert agent.stage_name == "generation"


class TestGeneratorAgentHealthCheck:
    """Tests for GeneratorAgent health check."""

    @pytest.mark.asyncio
    async def test_health_check_returns_true(self):
        """Health check returns True when templates are available."""
        agent = GeneratorAgent()
        result = await agent.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_all_formats(self):
        """Health check passes for all output formats."""
        for fmt in OutputFormat:
            agent = GeneratorAgent(output_format=fmt)
            result = await agent.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_generate_figma(self, sample_tokens):
        """Figma format should produce JSON-like output."""
        agent = GeneratorAgent(output_format=OutputFormat.FIGMA)
        output = await agent.generate(sample_tokens)
        assert '"version": "1.0"' in output
        assert "collections" in output


class TestGeneratorAgentProcess:
    """Tests for GeneratorAgent process method."""

    @pytest.fixture
    def sample_task(self):
        """Create a sample pipeline task."""
        return PipelineTask(
            task_id="test-task-001",
            image_url="https://example.com/image.png",
            token_types=[TokenType.COLOR, TokenType.SPACING],
        )

    @pytest.fixture
    def sample_tokens(self):
        """Create sample token results for testing."""
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                path=["color", "brand"],
                w3c_type=W3CTokenType.COLOR,
                value="#FF6B35",
                confidence=0.95,
                description="Primary brand color",
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                path=["color", "brand"],
                w3c_type=W3CTokenType.COLOR,
                value="#004E89",
                confidence=0.90,
                description="Secondary brand color",
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="small",
                path=["spacing"],
                w3c_type=W3CTokenType.DIMENSION,
                value="8px",
                confidence=0.88,
                description="Small spacing unit",
            ),
        ]

    @pytest.mark.asyncio
    async def test_process_returns_token_results(self, sample_task, sample_tokens):
        """Process returns list of TokenResult objects."""
        agent = GeneratorAgent()
        results = await agent.process(sample_task, tokens=sample_tokens)
        assert isinstance(results, list)
        # Generator returns the generated output as metadata in results
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_process_without_tokens_raises(self, sample_task):
        """Process without tokens raises GenerationError."""
        agent = GeneratorAgent()
        with pytest.raises(GenerationError, match="No tokens provided"):
            await agent.process(sample_task)

    @pytest.mark.asyncio
    async def test_process_with_empty_tokens(self, sample_task):
        """Process with empty token list returns empty result."""
        agent = GeneratorAgent()
        results = await agent.process(sample_task, tokens=[])
        assert results == []


class TestGeneratorAgentGenerate:
    """Tests for GeneratorAgent generate method."""

    @pytest.fixture
    def sample_tokens(self):
        """Create sample token results for testing."""
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                path=["color", "brand"],
                w3c_type=W3CTokenType.COLOR,
                value="#FF6B35",
                confidence=0.95,
                description="Primary brand color",
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                path=["color", "brand"],
                w3c_type=W3CTokenType.COLOR,
                value="#004E89",
                confidence=0.90,
            ),
        ]

    @pytest.mark.asyncio
    async def test_generate_returns_string(self, sample_tokens):
        """Generate method returns string output."""
        agent = GeneratorAgent()
        output = await agent.generate(sample_tokens)
        assert isinstance(output, str)

    @pytest.mark.asyncio
    async def test_generate_with_all_formats(self, sample_tokens):
        """Generate works with all output formats."""
        for fmt in OutputFormat:
            agent = GeneratorAgent(output_format=fmt)
            output = await agent.generate(sample_tokens)
            assert isinstance(output, str)
            assert len(output) > 0

    @pytest.mark.asyncio
    async def test_generate_empty_tokens_returns_empty(self):
        """Generate with empty tokens returns empty or minimal output."""
        agent = GeneratorAgent()
        output = await agent.generate([])
        assert isinstance(output, str)


class TestGeneratorAgentFormatSwitch:
    """Tests for switching output formats."""

    @pytest.fixture
    def sample_tokens(self):
        """Create sample token results."""
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                path=["color"],
                w3c_type=W3CTokenType.COLOR,
                value="#FF6B35",
                confidence=0.95,
            ),
        ]

    def test_set_format(self, sample_tokens):
        """Agent format can be changed."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        agent.output_format = OutputFormat.CSS
        assert agent.output_format == OutputFormat.CSS

    @pytest.mark.asyncio
    async def test_generate_with_format_override(self, sample_tokens):
        """Generate can use format override."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(sample_tokens, output_format=OutputFormat.CSS)
        assert "--color-primary" in output


class TestGeneratorAgentTokenGrouping:
    """Tests for token grouping in output."""

    @pytest.fixture
    def mixed_tokens(self):
        """Create tokens with mixed types and paths."""
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                path=["color", "brand"],
                w3c_type=W3CTokenType.COLOR,
                value="#FF6B35",
                confidence=0.95,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="secondary",
                path=["color", "brand"],
                w3c_type=W3CTokenType.COLOR,
                value="#004E89",
                confidence=0.90,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="success",
                path=["color", "semantic"],
                w3c_type=W3CTokenType.COLOR,
                value="#2ECC71",
                confidence=0.85,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="small",
                path=["spacing"],
                w3c_type=W3CTokenType.DIMENSION,
                value="8px",
                confidence=0.88,
            ),
        ]

    @pytest.mark.asyncio
    async def test_tokens_grouped_by_path(self, mixed_tokens):
        """Tokens are properly grouped by path in W3C output."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(mixed_tokens)
        # W3C output should maintain hierarchy
        assert "color" in output
        assert "brand" in output
        assert "semantic" in output
        assert "spacing" in output


class TestGeneratorAgentTemplateErrors:
    """Tests for template error handling."""

    @pytest.mark.asyncio
    async def test_invalid_token_data_raises_generation_error(self):
        """Invalid token data raises GenerationError."""
        agent = GeneratorAgent()
        # Create a token with problematic value
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="test",
                value={"nested": {"deep": object()}},  # Non-serializable
                confidence=0.5,
            ),
        ]
        # Should handle gracefully or raise GenerationError
        with pytest.raises((GenerationError, TypeError)):
            await agent.generate(tokens)


class TestGeneratorAgentReferenceTokens:
    """Tests for tokens with references."""

    @pytest.fixture
    def reference_tokens(self):
        """Create tokens with references."""
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                path=["color"],
                w3c_type=W3CTokenType.COLOR,
                value="#FF6B35",
                confidence=0.95,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="button-bg",
                path=["color", "button"],
                w3c_type=W3CTokenType.COLOR,
                value="",
                reference="{color.primary}",
                confidence=0.90,
            ),
        ]

    @pytest.mark.asyncio
    async def test_w3c_includes_references(self, reference_tokens):
        """W3C output includes token references."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(reference_tokens)
        assert "{color.primary}" in output

    @pytest.mark.asyncio
    async def test_css_resolves_references(self, reference_tokens):
        """CSS output uses CSS var() for references."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(reference_tokens)
        assert "var(--color-primary)" in output


class TestGeneratorAgentEmptyOutputFormats:
    """Tests for empty output in different formats."""

    @pytest.mark.asyncio
    async def test_empty_output_css(self):
        """CSS empty output has correct format."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate([])
        assert ":root {" in output

    @pytest.mark.asyncio
    async def test_empty_output_scss(self):
        """SCSS empty output has correct format."""
        agent = GeneratorAgent(output_format=OutputFormat.SCSS)
        output = await agent.generate([])
        assert "No tokens" in output

    @pytest.mark.asyncio
    async def test_empty_output_react(self):
        """React empty output has correct format."""
        agent = GeneratorAgent(output_format=OutputFormat.REACT)
        output = await agent.generate([])
        assert "export const tokens" in output

    @pytest.mark.asyncio
    async def test_empty_output_tailwind(self):
        """Tailwind empty output has correct format."""
        agent = GeneratorAgent(output_format=OutputFormat.TAILWIND)
        output = await agent.generate([])
        assert "module.exports" in output


class TestGeneratorAgentHealthCheckFailure:
    """Tests for health check failure scenarios."""

    @pytest.mark.asyncio
    async def test_health_check_fails_when_template_missing(self, tmp_path, monkeypatch):
        """Health check fails when template is missing."""
        agent = GeneratorAgent()
        # Point to a directory without templates
        monkeypatch.setattr(agent, "_template_dir", tmp_path)
        result = await agent.health_check()
        assert result is False


class TestGeneratorAgentInternalMethods:
    """Tests for internal utility methods."""

    def test_to_kebab_case_with_string(self):
        """_to_kebab_case handles string input."""
        result = GeneratorAgent._to_kebab_case("my_variable.name")
        assert result == "my-variable-name"

    def test_to_kebab_case_with_list(self):
        """_to_kebab_case handles list input."""
        result = GeneratorAgent._to_kebab_case(["color", "brand", "primary"])
        assert result == "color-brand-primary"

    def test_to_camel_case_with_dashes(self):
        """_to_camel_case handles dashes."""
        result = GeneratorAgent._to_camel_case("my-variable-name")
        assert result == "myVariableName"

    def test_to_camel_case_with_underscores(self):
        """_to_camel_case handles underscores."""
        result = GeneratorAgent._to_camel_case("my_variable_name")
        assert result == "myVariableName"

    def test_resolve_reference_empty(self):
        """_resolve_reference handles empty reference."""
        result = GeneratorAgent._resolve_reference("")
        assert result == ""

    def test_resolve_reference_css(self):
        """_resolve_reference handles CSS format."""
        result = GeneratorAgent._resolve_reference("{color.primary}", "css")
        assert result == "var(--color-primary)"

    def test_resolve_reference_scss(self):
        """_resolve_reference handles SCSS format."""
        result = GeneratorAgent._resolve_reference("{color.primary}", "scss")
        assert result == "$color-primary"

    def test_resolve_reference_other_format(self):
        """_resolve_reference returns original for unknown format."""
        result = GeneratorAgent._resolve_reference("{color.primary}", "other")
        assert result == "{color.primary}"

    def test_shadow_to_css_non_dict(self):
        """_shadow_to_css handles non-dict input."""
        result = GeneratorAgent._shadow_to_css("0 4px 8px black")
        assert result == "0 4px 8px black"

    def test_shadow_to_css_dict(self):
        """_shadow_to_css converts dict to CSS string."""
        shadow = {
            "offsetX": "0px",
            "offsetY": "4px",
            "blur": "8px",
            "spread": "0px",
            "color": "rgba(0,0,0,0.2)",
        }
        result = GeneratorAgent._shadow_to_css(shadow)
        assert "0px" in result
        assert "4px" in result
        assert "8px" in result
        assert "rgba(0,0,0,0.2)" in result


class TestGeneratorAgentTemplateLoadErrors:
    """Tests for template loading errors."""

    @pytest.mark.asyncio
    async def test_missing_template_raises_generation_error(self, tmp_path, monkeypatch):
        """Missing template raises GenerationError."""
        from jinja2 import Environment, FileSystemLoader

        agent = GeneratorAgent()
        # Create environment with empty template directory
        empty_env = Environment(loader=FileSystemLoader(str(tmp_path)))
        monkeypatch.setattr(agent, "_env", empty_env)

        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="test",
                value="#FF0000",
                confidence=0.9,
            ),
        ]
        with pytest.raises(GenerationError, match="Failed to load template"):
            await agent.generate(tokens)
