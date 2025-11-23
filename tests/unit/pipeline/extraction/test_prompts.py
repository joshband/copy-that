"""Tests for extraction prompts module."""

import pytest

from copy_that.pipeline import TokenType
from copy_that.pipeline.extraction.prompts import (
    PROMPT_REGISTRY,
    SYSTEM_PROMPT,
    get_extraction_prompt,
    get_system_prompt,
)


class TestGetSystemPrompt:
    """Tests for get_system_prompt function."""

    def test_returns_system_prompt(self):
        """Test that get_system_prompt returns the system prompt."""
        result = get_system_prompt()
        assert result == SYSTEM_PROMPT

    def test_returns_string(self):
        """Test that get_system_prompt returns a string."""
        result = get_system_prompt()
        assert isinstance(result, str)

    def test_contains_guidelines(self):
        """Test that system prompt contains guidelines."""
        result = get_system_prompt()
        assert "Guidelines:" in result


class TestGetExtractionPrompt:
    """Tests for get_extraction_prompt function."""

    def test_get_color_prompt(self):
        """Test getting color extraction prompt."""
        result = get_extraction_prompt(TokenType.COLOR)
        assert "extract_colors" in result

    def test_get_spacing_prompt(self):
        """Test getting spacing extraction prompt."""
        result = get_extraction_prompt(TokenType.SPACING)
        assert "extract_spacing" in result

    def test_get_typography_prompt(self):
        """Test getting typography extraction prompt."""
        result = get_extraction_prompt(TokenType.TYPOGRAPHY)
        assert "extract_typography" in result

    def test_get_shadow_prompt(self):
        """Test getting shadow extraction prompt."""
        result = get_extraction_prompt(TokenType.SHADOW)
        assert "extract_shadows" in result

    def test_get_gradient_prompt(self):
        """Test getting gradient extraction prompt."""
        result = get_extraction_prompt(TokenType.GRADIENT)
        assert "extract_gradients" in result

    def test_get_prompt_with_string_token_type(self):
        """Test getting prompt with string token type."""
        result = get_extraction_prompt("color")
        assert "extract_colors" in result

    def test_get_prompt_with_string_spacing(self):
        """Test getting spacing prompt with string."""
        result = get_extraction_prompt("spacing")
        assert "extract_spacing" in result

    def test_invalid_string_raises_value_error(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            get_extraction_prompt("invalid_type")

    def test_all_token_types_have_prompts(self):
        """Test that all token types have prompts in registry."""
        for token_type in TokenType:
            assert token_type in PROMPT_REGISTRY
            result = get_extraction_prompt(token_type)
            assert isinstance(result, str)
            assert len(result) > 0


class TestPromptRegistry:
    """Tests for prompt registry."""

    def test_registry_has_all_token_types(self):
        """Test that registry contains all token types."""
        assert len(PROMPT_REGISTRY) == len(TokenType)

    def test_all_prompts_are_strings(self):
        """Test that all prompts are strings."""
        for prompt in PROMPT_REGISTRY.values():
            assert isinstance(prompt, str)

    def test_all_prompts_mention_tool(self):
        """Test that all prompts mention their tool."""
        tool_names = {
            TokenType.COLOR: "extract_colors",
            TokenType.SPACING: "extract_spacing",
            TokenType.TYPOGRAPHY: "extract_typography",
            TokenType.SHADOW: "extract_shadows",
            TokenType.GRADIENT: "extract_gradients",
        }
        for token_type, tool_name in tool_names.items():
            assert tool_name in PROMPT_REGISTRY[token_type]
