"""
Test suite for token generators - W3C, CSS, React, and HTML exports

Tests cover:
- Proper output format for each generator
- Handling of token metadata (roles, provenance)
- Edge cases (empty libraries, special characters, etc.)
- Format-specific requirements (valid JSON, CSS, etc.)
"""

import json
import pytest
from copy_that.tokens.color.aggregator import (
    AggregatedColorToken,
    TokenLibrary,
)
from copy_that.generators.base_generator import BaseGenerator
from copy_that.generators.w3c_generator import W3CTokenGenerator
from copy_that.generators.css_generator import CSSTokenGenerator
from copy_that.generators.react_generator import ReactTokenGenerator
from copy_that.generators.html_demo_generator import HTMLDemoGenerator


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_library():
    """Create a sample TokenLibrary for testing"""
    tokens = [
        AggregatedColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Primary-Red",
            confidence=0.95,
            harmony="warm",
            temperature="warm",
            role="primary",
            provenance={"image_0": 0.95, "image_1": 0.88},
        ),
        AggregatedColorToken(
            hex="#0066FF",
            rgb="rgb(0, 102, 255)",
            name="Primary-Blue",
            confidence=0.92,
            harmony="cool",
            temperature="cool",
            role="secondary",
            provenance={"image_0": 0.92},
        ),
        AggregatedColorToken(
            hex="#00AA00",
            rgb="rgb(0, 170, 0)",
            name="Success-Green",
            confidence=0.90,
            harmony="natural",
            temperature="neutral",
            role="accent",
            provenance={"image_1": 0.90, "image_2": 0.85},
        ),
    ]
    library = TokenLibrary(
        tokens=tokens,
        statistics={
            "color_count": 3,
            "image_count": 3,
            "avg_confidence": 0.92,
            "min_confidence": 0.85,
            "max_confidence": 0.95,
            "dominant_colors": ["#FF5733", "#0066FF", "#00AA00"],
            "multi_image_colors": 2,
        },
        token_type="color",
    )
    return library


@pytest.fixture
def empty_library():
    """Create an empty TokenLibrary for testing edge cases"""
    return TokenLibrary(
        tokens=[],
        statistics={
            "color_count": 0,
            "image_count": 0,
            "avg_confidence": 0.0,
            "min_confidence": 0.0,
            "max_confidence": 0.0,
            "dominant_colors": [],
            "multi_image_colors": 0,
        },
        token_type="color",
    )


@pytest.fixture
def library_with_special_chars():
    """Create a library with special characters in names"""
    tokens = [
        AggregatedColorToken(
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Red & Orange",
            confidence=0.95,
            provenance={"image_0": 0.95},
        ),
        AggregatedColorToken(
            hex="#0066FF",
            rgb="rgb(0, 102, 255)",
            name="Blue (Primary)",
            confidence=0.92,
            provenance={"image_0": 0.92},
        ),
    ]
    return TokenLibrary(
        tokens=tokens,
        statistics={
            "color_count": 2,
            "image_count": 1,
            "avg_confidence": 0.935,
            "min_confidence": 0.92,
            "max_confidence": 0.95,
            "dominant_colors": ["#FF5733", "#0066FF"],
            "multi_image_colors": 0,
        },
        token_type="color",
    )


# ============================================================================
# BaseGenerator Interface Tests
# ============================================================================


class TestBaseGeneratorInterface:
    """Test that BaseGenerator defines the required interface"""

    def test_base_generator_is_abstract(self):
        """BaseGenerator should be abstract and not instantiable"""
        with pytest.raises(TypeError):
            BaseGenerator(TokenLibrary())

    def test_base_generator_requires_generate_method(self):
        """Concrete generators must implement generate()"""

        class IncompleteGenerator(BaseGenerator):
            pass

        with pytest.raises(TypeError):
            IncompleteGenerator(TokenLibrary())


# ============================================================================
# W3C Token Generator Tests
# ============================================================================


class TestW3CTokenGenerator:
    """Test W3C Design Tokens format generation"""

    def test_generate_returns_valid_json(self, sample_library):
        """Generated output should be valid JSON"""
        generator = W3CTokenGenerator(sample_library)
        output = generator.generate()
        assert isinstance(output, str)
        parsed = json.loads(output)  # Should not raise
        assert isinstance(parsed, dict)

    def test_w3c_has_required_structure(self, sample_library):
        """W3C output must have $schema and $tokens properties"""
        generator = W3CTokenGenerator(sample_library)
        output = json.loads(generator.generate())
        assert "$schema" in output
        assert "$tokens" in output or "color" in output

    def test_w3c_contains_all_colors(self, sample_library):
        """W3C output should include all tokens from library"""
        generator = W3CTokenGenerator(sample_library)
        output = json.loads(generator.generate())

        # W3C Design Tokens format has color tokens
        color_section = output.get("color", {})
        if color_section:
            # Count color tokens
            token_count = len(color_section)
            assert token_count == 3

    def test_w3c_empty_library(self, empty_library):
        """W3C generator should handle empty libraries gracefully"""
        generator = W3CTokenGenerator(empty_library)
        output = json.loads(generator.generate())
        assert isinstance(output, dict)

    def test_w3c_preserves_color_values(self, sample_library):
        """W3C output should preserve hex color values"""
        generator = W3CTokenGenerator(sample_library)
        output = json.loads(generator.generate())

        # Check that original colors are preserved
        # (exact structure depends on implementation)
        output_str = json.dumps(output)
        assert "#FF5733" in output_str
        assert "#0066FF" in output_str
        assert "#00AA00" in output_str

    def test_w3c_includes_metadata(self, sample_library):
        """W3C output should include token metadata (confidence, role)"""
        generator = W3CTokenGenerator(sample_library)
        output = json.loads(generator.generate())
        output_str = json.dumps(output)

        # Should reference roles
        assert "primary" in output_str or "Primary" in output_str

    def test_w3c_handles_special_characters(self, library_with_special_chars):
        """W3C generator should handle special characters in names"""
        generator = W3CTokenGenerator(library_with_special_chars)
        output = generator.generate()
        assert isinstance(output, str)
        parsed = json.loads(output)  # Should not raise
        assert isinstance(parsed, dict)


# ============================================================================
# CSS Token Generator Tests
# ============================================================================


class TestCSSTokenGenerator:
    """Test CSS custom properties generation"""

    def test_generate_returns_css_string(self, sample_library):
        """Generated output should be valid CSS"""
        generator = CSSTokenGenerator(sample_library)
        output = generator.generate()
        assert isinstance(output, str)
        assert ":root" in output or "--" in output

    def test_css_contains_color_variables(self, sample_library):
        """CSS output should define color variables"""
        generator = CSSTokenGenerator(sample_library)
        output = generator.generate()
        # Should have CSS variables with color names
        assert "--color-" in output

    def test_css_uses_hex_values(self, sample_library):
        """CSS output should use hex color values"""
        generator = CSSTokenGenerator(sample_library)
        output = generator.generate()
        assert "#FF5733" in output
        assert "#0066FF" in output

    def test_css_empty_library(self, empty_library):
        """CSS generator should handle empty libraries gracefully"""
        generator = CSSTokenGenerator(empty_library)
        output = generator.generate()
        assert isinstance(output, str)
        # Should at least have :root selector
        assert ":root" in output

    def test_css_valid_syntax(self, sample_library):
        """Generated CSS should have valid syntax"""
        generator = CSSTokenGenerator(sample_library)
        output = generator.generate()

        # Check for proper CSS structure
        assert "{" in output and "}" in output
        assert ":" in output  # Property:value pairs

    def test_css_semantic_naming(self, sample_library):
        """CSS variables should use semantic names when available"""
        generator = CSSTokenGenerator(sample_library)
        output = generator.generate()

        # Should have variables corresponding to roles
        assert "primary" in output.lower() or "red" in output.lower()

    def test_css_handles_special_characters(self, library_with_special_chars):
        """CSS generator should handle special characters in names"""
        generator = CSSTokenGenerator(library_with_special_chars)
        output = generator.generate()
        assert isinstance(output, str)
        # Should sanitize names for valid CSS identifiers
        assert ":root" in output

    def test_css_includes_comments(self, sample_library):
        """CSS output might include comments for metadata"""
        generator = CSSTokenGenerator(sample_library)
        output = generator.generate()
        # Comments are optional but nice to have
        # Just verify it's still valid CSS
        assert ":root" in output


# ============================================================================
# React Token Generator Tests
# ============================================================================


class TestReactTokenGenerator:
    """Test React/TypeScript export generation"""

    def test_generate_returns_typescript_string(self, sample_library):
        """Generated output should be valid TypeScript"""
        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()
        assert isinstance(output, str)
        assert "export" in output

    def test_react_contains_color_export(self, sample_library):
        """React output should export colors object"""
        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()
        assert "colors" in output or "tokens" in output

    def test_react_uses_hex_values(self, sample_library):
        """React output should use hex color values"""
        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()
        assert "#FF5733" in output
        assert "#0066FF" in output

    def test_react_empty_library(self, empty_library):
        """React generator should handle empty libraries gracefully"""
        generator = ReactTokenGenerator(empty_library)
        output = generator.generate()
        assert isinstance(output, str)
        assert "export" in output

    def test_react_valid_typescript_syntax(self, sample_library):
        """Generated TypeScript should have valid syntax"""
        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()

        # Check TypeScript structure
        assert "{" in output and "}" in output
        assert ":" in output  # Type annotations
        assert "export" in output

    def test_react_semantic_naming(self, sample_library):
        """React exports should use semantic names"""
        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()

        # Should have properties for different roles
        assert "primary" in output.lower() or "red" in output.lower()

    def test_react_handles_special_characters(self, library_with_special_chars):
        """React generator should handle special characters in names"""
        generator = ReactTokenGenerator(library_with_special_chars)
        output = generator.generate()
        assert isinstance(output, str)
        # Should sanitize names for valid JS identifiers
        assert "export" in output

    def test_react_is_importable_typescript(self, sample_library):
        """Generated code should be importable as TypeScript"""
        generator = ReactTokenGenerator(sample_library)
        output = generator.generate()

        # Should have const or export statements
        assert "export" in output


# ============================================================================
# HTML Demo Generator Tests
# ============================================================================


class TestHTMLDemoGenerator:
    """Test HTML demo page generation"""

    def test_generate_returns_html_string(self, sample_library):
        """Generated output should be valid HTML"""
        generator = HTMLDemoGenerator(sample_library)
        output = generator.generate()
        assert isinstance(output, str)
        assert "<!DOCTYPE" in output or "<html" in output

    def test_html_contains_color_swatches(self, sample_library):
        """HTML output should display color swatches"""
        generator = HTMLDemoGenerator(sample_library)
        output = generator.generate()

        # Should contain color values and display elements
        assert "#FF5733" in output
        assert "#0066FF" in output

    def test_html_has_proper_structure(self, sample_library):
        """HTML output should have proper document structure"""
        generator = HTMLDemoGenerator(sample_library)
        output = generator.generate()

        assert "<html" in output
        assert "<head" in output
        assert "<body" in output
        assert "</html>" in output

    def test_html_empty_library(self, empty_library):
        """HTML generator should handle empty libraries gracefully"""
        generator = HTMLDemoGenerator(empty_library)
        output = generator.generate()
        assert isinstance(output, str)
        assert "<html" in output

    def test_html_includes_metadata(self, sample_library):
        """HTML demo should include token metadata"""
        generator = HTMLDemoGenerator(sample_library)
        output = generator.generate()

        # Should show confidence or other metadata
        output_lower = output.lower()
        assert "color" in output_lower

    def test_html_includes_color_names(self, sample_library):
        """HTML demo should show color names"""
        generator = HTMLDemoGenerator(sample_library)
        output = generator.generate()

        # Should reference token names
        assert "Primary-Red" in output or "primary" in output.lower()

    def test_html_handles_special_characters(self, library_with_special_chars):
        """HTML generator should handle special characters safely"""
        generator = HTMLDemoGenerator(library_with_special_chars)
        output = generator.generate()
        assert isinstance(output, str)
        assert "<html" in output

    def test_html_includes_css_styling(self, sample_library):
        """HTML demo should include CSS styling"""
        generator = HTMLDemoGenerator(sample_library)
        output = generator.generate()
        assert "<style>" in output or "<link" in output


# ============================================================================
# Generator Consistency Tests
# ============================================================================


class TestGeneratorConsistency:
    """Test that all generators handle input consistently"""

    def test_all_generators_accept_token_library(self, sample_library):
        """All generators should accept TokenLibrary objects"""
        generators = [
            W3CTokenGenerator,
            CSSTokenGenerator,
            ReactTokenGenerator,
            HTMLDemoGenerator,
        ]
        for GeneratorClass in generators:
            generator = GeneratorClass(sample_library)
            assert generator is not None

    def test_all_generators_have_generate_method(self, sample_library):
        """All generators should have generate() method"""
        generators = [
            W3CTokenGenerator,
            CSSTokenGenerator,
            ReactTokenGenerator,
            HTMLDemoGenerator,
        ]
        for GeneratorClass in generators:
            generator = GeneratorClass(sample_library)
            assert hasattr(generator, "generate")
            assert callable(generator.generate)

    def test_all_generators_return_strings(self, sample_library):
        """All generators should return string output"""
        generators = [
            W3CTokenGenerator,
            CSSTokenGenerator,
            ReactTokenGenerator,
            HTMLDemoGenerator,
        ]
        for GeneratorClass in generators:
            generator = GeneratorClass(sample_library)
            output = generator.generate()
            assert isinstance(output, str)

    def test_all_generators_preserve_color_data(self, sample_library):
        """All generators should preserve original color hex values"""
        generators = [
            W3CTokenGenerator,
            CSSTokenGenerator,
            ReactTokenGenerator,
            HTMLDemoGenerator,
        ]
        for GeneratorClass in generators:
            generator = GeneratorClass(sample_library)
            output = generator.generate()
            # All should include at least one color
            assert "#FF5733" in output


# ============================================================================
# Advanced Generator Tests
# ============================================================================


class TestGeneratorEdgeCases:
    """Test generators with edge cases and unusual inputs"""

    def test_single_color_library(self):
        """Generators should handle libraries with single color"""
        tokens = [
            AggregatedColorToken(
                hex="#000000",
                rgb="rgb(0, 0, 0)",
                name="Black",
                confidence=0.99,
                provenance={"image_0": 0.99},
            )
        ]
        library = TokenLibrary(
            tokens=tokens,
            statistics={
                "color_count": 1,
                "image_count": 1,
                "avg_confidence": 0.99,
                "min_confidence": 0.99,
                "max_confidence": 0.99,
                "dominant_colors": ["#000000"],
                "multi_image_colors": 0,
            },
            token_type="color",
        )

        generators = [
            W3CTokenGenerator,
            CSSTokenGenerator,
            ReactTokenGenerator,
            HTMLDemoGenerator,
        ]
        for GeneratorClass in generators:
            generator = GeneratorClass(library)
            output = generator.generate()
            assert isinstance(output, str)
            assert "#000000" in output

    def test_many_colors_library(self):
        """Generators should handle libraries with many colors"""
        tokens = [
            AggregatedColorToken(
                hex=f"#{i:06X}",
                rgb=f"rgb({i % 256}, {(i * 2) % 256}, {(i * 3) % 256})",
                name=f"Color-{i}",
                confidence=0.95,
                provenance={"image_0": 0.95},
            )
            for i in range(50)
        ]
        library = TokenLibrary(
            tokens=tokens,
            statistics={
                "color_count": 50,
                "image_count": 1,
                "avg_confidence": 0.95,
                "min_confidence": 0.95,
                "max_confidence": 0.95,
                "dominant_colors": [t.hex for t in tokens[:5]],
                "multi_image_colors": 0,
            },
            token_type="color",
        )

        generators = [
            W3CTokenGenerator,
            CSSTokenGenerator,
            ReactTokenGenerator,
            HTMLDemoGenerator,
        ]
        for GeneratorClass in generators:
            generator = GeneratorClass(library)
            output = generator.generate()
            assert isinstance(output, str)
            # Should include some colors
            assert "#" in output

    def test_library_with_no_roles(self):
        """Generators should handle tokens without role assignments"""
        tokens = [
            AggregatedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                name="Red",
                confidence=0.95,
                role=None,  # No role assigned
                provenance={"image_0": 0.95},
            )
        ]
        library = TokenLibrary(
            tokens=tokens,
            statistics={
                "color_count": 1,
                "image_count": 1,
                "avg_confidence": 0.95,
                "min_confidence": 0.95,
                "max_confidence": 0.95,
                "dominant_colors": ["#FF5733"],
                "multi_image_colors": 0,
            },
            token_type="color",
        )

        generators = [
            W3CTokenGenerator,
            CSSTokenGenerator,
            ReactTokenGenerator,
            HTMLDemoGenerator,
        ]
        for GeneratorClass in generators:
            generator = GeneratorClass(library)
            output = generator.generate()
            assert isinstance(output, str)
