"""
Tests for output format generation.

Tests specific output format correctness including:
- W3C Design Tokens JSON
- CSS Custom Properties
- SCSS Variables
- React theme object
- Tailwind configuration
"""

import json

import pytest

from copy_that.pipeline import TokenResult, TokenType, W3CTokenType
from copy_that.pipeline.generator import GeneratorAgent, OutputFormat


@pytest.fixture
def color_tokens():
    """Create color token results for testing."""
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
            token_type=TokenType.COLOR,
            name="success",
            path=["color", "semantic"],
            w3c_type=W3CTokenType.COLOR,
            value="#2ECC71",
            confidence=0.85,
        ),
        TokenResult(
            token_type=TokenType.COLOR,
            name="error",
            path=["color", "semantic"],
            w3c_type=W3CTokenType.COLOR,
            value="#E74C3C",
            confidence=0.85,
        ),
    ]


@pytest.fixture
def spacing_tokens():
    """Create spacing token results for testing."""
    return [
        TokenResult(
            token_type=TokenType.SPACING,
            name="xs",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="4px",
            confidence=0.90,
        ),
        TokenResult(
            token_type=TokenType.SPACING,
            name="sm",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="8px",
            confidence=0.88,
        ),
        TokenResult(
            token_type=TokenType.SPACING,
            name="md",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="16px",
            confidence=0.92,
        ),
        TokenResult(
            token_type=TokenType.SPACING,
            name="lg",
            path=["spacing"],
            w3c_type=W3CTokenType.DIMENSION,
            value="32px",
            confidence=0.87,
        ),
    ]


@pytest.fixture
def typography_tokens():
    """Create typography token results for testing."""
    return [
        TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="heading",
            path=["font", "family"],
            w3c_type=W3CTokenType.FONT_FAMILY,
            value="Inter, sans-serif",
            confidence=0.85,
        ),
        TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="body",
            path=["font", "family"],
            w3c_type=W3CTokenType.FONT_FAMILY,
            value="Roboto, sans-serif",
            confidence=0.82,
        ),
        TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="bold",
            path=["font", "weight"],
            w3c_type=W3CTokenType.FONT_WEIGHT,
            value=700,
            confidence=0.90,
        ),
    ]


@pytest.fixture
def mixed_tokens(color_tokens, spacing_tokens, typography_tokens):
    """Create mixed token results for testing."""
    return color_tokens + spacing_tokens + typography_tokens


class TestW3CFormat:
    """Tests for W3C Design Tokens JSON format."""

    @pytest.mark.asyncio
    async def test_w3c_valid_json(self, color_tokens):
        """W3C output is valid JSON."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(color_tokens)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_w3c_nested_structure(self, color_tokens):
        """W3C output has nested structure based on paths."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(color_tokens)
        parsed = json.loads(output)

        # Should have color.brand.primary structure
        assert "color" in parsed
        assert "brand" in parsed["color"]
        assert "primary" in parsed["color"]["brand"]

    @pytest.mark.asyncio
    async def test_w3c_token_has_value(self, color_tokens):
        """W3C tokens have $value field."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(color_tokens)
        parsed = json.loads(output)

        primary = parsed["color"]["brand"]["primary"]
        assert "$value" in primary
        assert primary["$value"] == "#FF6B35"

    @pytest.mark.asyncio
    async def test_w3c_token_has_type(self, color_tokens):
        """W3C tokens have $type field."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(color_tokens)
        parsed = json.loads(output)

        primary = parsed["color"]["brand"]["primary"]
        assert "$type" in primary
        assert primary["$type"] == "color"

    @pytest.mark.asyncio
    async def test_w3c_token_has_description(self, color_tokens):
        """W3C tokens include $description when present."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(color_tokens)
        parsed = json.loads(output)

        primary = parsed["color"]["brand"]["primary"]
        assert "$description" in primary
        assert primary["$description"] == "Primary brand color"

    @pytest.mark.asyncio
    async def test_w3c_token_has_extensions(self, color_tokens):
        """W3C tokens have $extensions with metadata."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(color_tokens)
        parsed = json.loads(output)

        primary = parsed["color"]["brand"]["primary"]
        assert "$extensions" in primary
        assert "com.copythat" in primary["$extensions"]
        assert "confidence" in primary["$extensions"]["com.copythat"]

    @pytest.mark.asyncio
    async def test_w3c_multiple_token_types(self, mixed_tokens):
        """W3C output handles multiple token types."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(mixed_tokens)
        parsed = json.loads(output)

        assert "color" in parsed
        assert "spacing" in parsed
        assert "font" in parsed


class TestCSSFormat:
    """Tests for CSS Custom Properties format."""

    @pytest.mark.asyncio
    async def test_css_root_selector(self, color_tokens):
        """CSS output has :root selector."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(color_tokens)
        assert ":root {" in output

    @pytest.mark.asyncio
    async def test_css_custom_properties(self, color_tokens):
        """CSS output uses custom property syntax."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(color_tokens)
        assert "--color-brand-primary" in output
        assert "#FF6B35" in output

    @pytest.mark.asyncio
    async def test_css_naming_convention(self, color_tokens):
        """CSS variables use kebab-case from path."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(color_tokens)

        assert "--color-brand-primary" in output
        assert "--color-brand-secondary" in output
        assert "--color-semantic-success" in output

    @pytest.mark.asyncio
    async def test_css_comments_for_descriptions(self, color_tokens):
        """CSS includes comments for token descriptions."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(color_tokens)
        assert "Primary brand color" in output

    @pytest.mark.asyncio
    async def test_css_multiple_token_types(self, mixed_tokens):
        """CSS output handles multiple token types."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(mixed_tokens)

        assert "--color-brand-primary" in output
        assert "--spacing-xs" in output
        assert "--font-family-heading" in output


class TestSCSSFormat:
    """Tests for SCSS Variables format."""

    @pytest.mark.asyncio
    async def test_scss_variable_syntax(self, color_tokens):
        """SCSS output uses $ variable syntax."""
        agent = GeneratorAgent(output_format=OutputFormat.SCSS)
        output = await agent.generate(color_tokens)
        assert "$color-brand-primary" in output
        assert "#FF6B35" in output

    @pytest.mark.asyncio
    async def test_scss_naming_convention(self, color_tokens):
        """SCSS variables use kebab-case from path."""
        agent = GeneratorAgent(output_format=OutputFormat.SCSS)
        output = await agent.generate(color_tokens)

        assert "$color-brand-primary" in output
        assert "$color-brand-secondary" in output
        assert "$color-semantic-success" in output

    @pytest.mark.asyncio
    async def test_scss_comments(self, color_tokens):
        """SCSS includes comments for descriptions."""
        agent = GeneratorAgent(output_format=OutputFormat.SCSS)
        output = await agent.generate(color_tokens)
        assert "Primary brand color" in output

    @pytest.mark.asyncio
    async def test_scss_maps_option(self, color_tokens):
        """SCSS can optionally generate maps."""
        agent = GeneratorAgent(output_format=OutputFormat.SCSS)
        output = await agent.generate(color_tokens, use_maps=True)
        # Should contain SCSS map syntax
        assert "$colors:" in output or "$color:" in output


class TestReactFormat:
    """Tests for React theme object format."""

    @pytest.mark.asyncio
    async def test_react_valid_typescript(self, color_tokens):
        """React output is valid TypeScript object."""
        agent = GeneratorAgent(output_format=OutputFormat.REACT)
        output = await agent.generate(color_tokens)

        # Should export a theme object
        assert "export" in output
        assert "theme" in output.lower() or "tokens" in output.lower()

    @pytest.mark.asyncio
    async def test_react_nested_structure(self, color_tokens):
        """React output has nested object structure."""
        agent = GeneratorAgent(output_format=OutputFormat.REACT)
        output = await agent.generate(color_tokens)

        assert "color:" in output or "color :" in output or '"color":' in output
        assert "brand:" in output or "brand :" in output or '"brand":' in output

    @pytest.mark.asyncio
    async def test_react_camelcase_keys(self, color_tokens):
        """React output uses camelCase for keys."""
        agent = GeneratorAgent(output_format=OutputFormat.REACT)
        output = await agent.generate(color_tokens)

        # Should not have kebab-case keys in the nested structure
        assert "--" not in output.replace("/**", "").replace("*/", "")

    @pytest.mark.asyncio
    async def test_react_type_annotations(self, color_tokens):
        """React output includes TypeScript type annotations."""
        agent = GeneratorAgent(output_format=OutputFormat.REACT)
        output = await agent.generate(color_tokens)

        # Should have type information
        assert "const" in output or "type" in output or "interface" in output

    @pytest.mark.asyncio
    async def test_react_multiple_token_types(self, mixed_tokens):
        """React output handles multiple token types."""
        agent = GeneratorAgent(output_format=OutputFormat.REACT)
        output = await agent.generate(mixed_tokens)

        assert "color" in output
        assert "spacing" in output
        assert "font" in output


class TestTailwindFormat:
    """Tests for Tailwind CSS configuration format."""

    @pytest.mark.asyncio
    async def test_tailwind_module_export(self, color_tokens):
        """Tailwind output exports module."""
        agent = GeneratorAgent(output_format=OutputFormat.TAILWIND)
        output = await agent.generate(color_tokens)

        assert "module.exports" in output or "export default" in output

    @pytest.mark.asyncio
    async def test_tailwind_theme_extend(self, color_tokens):
        """Tailwind output uses theme.extend structure."""
        agent = GeneratorAgent(output_format=OutputFormat.TAILWIND)
        output = await agent.generate(color_tokens)

        assert "theme" in output
        assert "extend" in output or "colors" in output

    @pytest.mark.asyncio
    async def test_tailwind_color_keys(self, color_tokens):
        """Tailwind output has proper color keys."""
        agent = GeneratorAgent(output_format=OutputFormat.TAILWIND)
        output = await agent.generate(color_tokens)

        # Tailwind uses nested objects for colors
        assert "primary" in output
        assert "#FF6B35" in output

    @pytest.mark.asyncio
    async def test_tailwind_spacing_keys(self, spacing_tokens):
        """Tailwind output has proper spacing keys."""
        agent = GeneratorAgent(output_format=OutputFormat.TAILWIND)
        output = await agent.generate(spacing_tokens)

        assert "spacing" in output
        assert "xs" in output or "4px" in output

    @pytest.mark.asyncio
    async def test_tailwind_multiple_token_types(self, mixed_tokens):
        """Tailwind output handles multiple token types."""
        agent = GeneratorAgent(output_format=OutputFormat.TAILWIND)
        output = await agent.generate(mixed_tokens)

        # Should have colors and spacing at minimum
        assert "colors" in output or "color" in output
        assert "spacing" in output


class TestReferenceTokenHandling:
    """Tests for token reference handling across formats."""

    @pytest.fixture
    def tokens_with_references(self):
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
                name="background",
                path=["color", "button"],
                w3c_type=W3CTokenType.COLOR,
                value="",
                reference="{color.primary}",
                confidence=0.90,
            ),
        ]

    @pytest.mark.asyncio
    async def test_w3c_preserves_references(self, tokens_with_references):
        """W3C format preserves reference syntax."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(tokens_with_references)
        parsed = json.loads(output)

        button_bg = parsed["color"]["button"]["background"]
        assert button_bg["$value"] == "{color.primary}"

    @pytest.mark.asyncio
    async def test_css_uses_var_for_references(self, tokens_with_references):
        """CSS format uses var() for references."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(tokens_with_references)

        assert "var(--color-primary)" in output

    @pytest.mark.asyncio
    async def test_scss_uses_variable_interpolation(self, tokens_with_references):
        """SCSS format uses variable interpolation for references."""
        agent = GeneratorAgent(output_format=OutputFormat.SCSS)
        output = await agent.generate(tokens_with_references)

        # Should reference the SCSS variable
        assert "$color-primary" in output


class TestCompositeTokens:
    """Tests for composite token handling."""

    @pytest.fixture
    def shadow_token(self):
        """Create a shadow composite token."""
        return [
            TokenResult(
                token_type=TokenType.SHADOW,
                name="card",
                path=["shadow"],
                w3c_type=W3CTokenType.SHADOW,
                value={
                    "color": "#00000033",
                    "offsetX": "0px",
                    "offsetY": "4px",
                    "blur": "8px",
                    "spread": "0px",
                },
                confidence=0.88,
                description="Card shadow",
            ),
        ]

    @pytest.mark.asyncio
    async def test_w3c_composite_value(self, shadow_token):
        """W3C format preserves composite value structure."""
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(shadow_token)
        parsed = json.loads(output)

        shadow = parsed["shadow"]["card"]
        assert "$value" in shadow
        assert isinstance(shadow["$value"], dict)
        assert "color" in shadow["$value"]

    @pytest.mark.asyncio
    async def test_css_composite_to_string(self, shadow_token):
        """CSS format converts composite to CSS string."""
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(shadow_token)

        # Shadow should be converted to CSS box-shadow syntax
        assert "--shadow-card" in output


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    @pytest.mark.asyncio
    async def test_empty_path_token(self):
        """Token with empty path is handled."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="accent",
                path=[],
                w3c_type=W3CTokenType.COLOR,
                value="#FF0000",
                confidence=0.90,
            ),
        ]
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(tokens)
        parsed = json.loads(output)

        assert "accent" in parsed

    @pytest.mark.asyncio
    async def test_deep_nesting_path(self):
        """Token with deep nesting is handled."""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="text",
                path=["color", "semantic", "state", "hover"],
                w3c_type=W3CTokenType.COLOR,
                value="#0000FF",
                confidence=0.85,
            ),
        ]
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(tokens)
        parsed = json.loads(output)

        # Navigate the nested structure
        assert parsed["color"]["semantic"]["state"]["hover"]["text"]["$value"] == "#0000FF"

    @pytest.mark.asyncio
    async def test_special_characters_in_name(self):
        """Token names with special characters are handled."""
        tokens = [
            TokenResult(
                token_type=TokenType.SPACING,
                name="1.5x",
                path=["spacing"],
                w3c_type=W3CTokenType.DIMENSION,
                value="12px",
                confidence=0.80,
            ),
        ]
        agent = GeneratorAgent(output_format=OutputFormat.CSS)
        output = await agent.generate(tokens)

        # Should escape or transform special characters
        assert "12px" in output

    @pytest.mark.asyncio
    async def test_numeric_value_token(self):
        """Numeric values are handled correctly."""
        tokens = [
            TokenResult(
                token_type=TokenType.TYPOGRAPHY,
                name="bold",
                path=["font", "weight"],
                w3c_type=W3CTokenType.FONT_WEIGHT,
                value=700,
                confidence=0.90,
            ),
        ]
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(tokens)
        parsed = json.loads(output)

        weight = parsed["font"]["weight"]["bold"]
        assert weight["$value"] == 700

    @pytest.mark.asyncio
    async def test_boolean_value_token(self):
        """Boolean values are handled correctly."""
        tokens = [
            TokenResult(
                token_type=TokenType.TYPOGRAPHY,
                name="italic",
                path=["font", "style"],
                w3c_type=W3CTokenType.NUMBER,
                value=True,
                confidence=0.75,
            ),
        ]
        agent = GeneratorAgent(output_format=OutputFormat.W3C)
        output = await agent.generate(tokens)
        parsed = json.loads(output)

        style = parsed["font"]["style"]["italic"]
        assert style["$value"] is True
