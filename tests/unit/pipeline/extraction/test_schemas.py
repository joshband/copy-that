"""Tests for Tool Use schemas.

Tests written BEFORE implementation (TDD approach).
"""

import json

import pytest
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate

from copy_that.pipeline import TokenType
from copy_that.pipeline.extraction.schemas import (
    SCHEMA_REGISTRY,
    ColorExtractionSchema,
    GradientExtractionSchema,
    ShadowExtractionSchema,
    SpacingExtractionSchema,
    TypographyExtractionSchema,
    get_all_schemas,
    get_tool_schema,
    validate_extraction_result,
)


class TestSchemaRegistry:
    """Test schema registry and retrieval."""

    def test_registry_contains_all_token_types(self):
        """Registry should have schemas for all token types."""
        for token_type in TokenType:
            assert token_type in SCHEMA_REGISTRY

    def test_get_tool_schema_returns_valid_schema(self):
        """get_tool_schema should return valid JSON Schema."""
        for token_type in TokenType:
            schema = get_tool_schema(token_type)
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema
            assert schema["input_schema"]["type"] == "object"

    def test_get_tool_schema_invalid_type_raises_error(self):
        """get_tool_schema should raise error for invalid type."""
        with pytest.raises(ValueError):
            get_tool_schema("invalid_type")

    def test_get_all_schemas_returns_all(self):
        """get_all_schemas should return schemas for all token types."""
        schemas = get_all_schemas()
        assert len(schemas) == len(TokenType)
        for schema in schemas:
            assert "name" in schema
            assert "input_schema" in schema


class TestColorExtractionSchema:
    """Test color extraction schema."""

    def test_schema_name(self):
        """Schema should have correct name."""
        schema = ColorExtractionSchema.get_tool_definition()
        assert schema["name"] == "extract_colors"

    def test_schema_has_required_fields(self):
        """Schema should have all required fields for color tokens."""
        schema = ColorExtractionSchema.get_tool_definition()
        input_schema = schema["input_schema"]
        properties = input_schema["properties"]["colors"]["items"]["properties"]

        # Required fields
        assert "name" in properties
        assert "hex_value" in properties
        assert "confidence" in properties

        # Optional but important
        assert "rgb" in properties
        assert "hsl" in properties
        assert "usage" in properties
        assert "category" in properties

    def test_valid_color_extraction_result(self):
        """Valid color extraction result should pass validation."""
        result = {
            "colors": [
                {
                    "name": "primary-blue",
                    "hex_value": "#0066CC",
                    "confidence": 0.95,
                    "rgb": {"r": 0, "g": 102, "b": 204},
                    "hsl": {"h": 210, "s": 100, "l": 40},
                    "usage": "Primary brand color",
                    "category": "brand",
                }
            ]
        }
        schema = ColorExtractionSchema.get_json_schema()
        validate(result, schema)

    def test_invalid_hex_value_fails(self):
        """Invalid hex value should fail validation."""
        result = {"colors": [{"name": "invalid", "hex_value": "not-a-hex", "confidence": 0.5}]}
        schema = ColorExtractionSchema.get_json_schema()
        with pytest.raises(JsonSchemaValidationError):
            validate(result, schema)

    def test_confidence_out_of_range_fails(self):
        """Confidence outside 0-1 should fail validation."""
        result = {
            "colors": [
                {
                    "name": "test",
                    "hex_value": "#FF0000",
                    "confidence": 1.5,  # Invalid
                }
            ]
        }
        schema = ColorExtractionSchema.get_json_schema()
        with pytest.raises(JsonSchemaValidationError):
            validate(result, schema)

    def test_missing_required_field_fails(self):
        """Missing required field should fail validation."""
        result = {
            "colors": [
                {
                    "name": "test",
                    # Missing hex_value and confidence
                }
            ]
        }
        schema = ColorExtractionSchema.get_json_schema()
        with pytest.raises(JsonSchemaValidationError):
            validate(result, schema)


class TestSpacingExtractionSchema:
    """Test spacing extraction schema."""

    def test_schema_name(self):
        """Schema should have correct name."""
        schema = SpacingExtractionSchema.get_tool_definition()
        assert schema["name"] == "extract_spacing"

    def test_schema_has_required_fields(self):
        """Schema should have all required fields for spacing tokens."""
        schema = SpacingExtractionSchema.get_tool_definition()
        input_schema = schema["input_schema"]
        properties = input_schema["properties"]["spacing"]["items"]["properties"]

        assert "name" in properties
        assert "value" in properties
        assert "unit" in properties
        assert "confidence" in properties

    def test_valid_spacing_extraction_result(self):
        """Valid spacing extraction result should pass validation."""
        result = {
            "spacing": [
                {
                    "name": "space-sm",
                    "value": 8,
                    "unit": "px",
                    "confidence": 0.88,
                    "usage": "Small spacing between elements",
                    "scale_position": 2,
                }
            ]
        }
        schema = SpacingExtractionSchema.get_json_schema()
        validate(result, schema)

    def test_invalid_unit_fails(self):
        """Invalid unit should fail validation."""
        result = {
            "spacing": [{"name": "test", "value": 10, "unit": "invalid-unit", "confidence": 0.5}]
        }
        schema = SpacingExtractionSchema.get_json_schema()
        with pytest.raises(JsonSchemaValidationError):
            validate(result, schema)


class TestTypographyExtractionSchema:
    """Test typography extraction schema."""

    def test_schema_name(self):
        """Schema should have correct name."""
        schema = TypographyExtractionSchema.get_tool_definition()
        assert schema["name"] == "extract_typography"

    def test_schema_has_required_fields(self):
        """Schema should have all required fields for typography tokens."""
        schema = TypographyExtractionSchema.get_tool_definition()
        input_schema = schema["input_schema"]
        properties = input_schema["properties"]["typography"]["items"]["properties"]

        assert "name" in properties
        assert "font_family" in properties
        assert "font_size" in properties
        assert "font_weight" in properties
        assert "line_height" in properties
        assert "confidence" in properties

    def test_valid_typography_extraction_result(self):
        """Valid typography extraction result should pass validation."""
        result = {
            "typography": [
                {
                    "name": "heading-1",
                    "font_family": "Inter",
                    "font_size": {"value": 32, "unit": "px"},
                    "font_weight": 700,
                    "line_height": {"value": 1.2, "unit": "em"},
                    "letter_spacing": {"value": -0.5, "unit": "px"},
                    "confidence": 0.92,
                    "usage": "Main page headings",
                }
            ]
        }
        schema = TypographyExtractionSchema.get_json_schema()
        validate(result, schema)

    def test_invalid_font_weight_fails(self):
        """Invalid font weight should fail validation."""
        result = {
            "typography": [
                {
                    "name": "test",
                    "font_family": "Arial",
                    "font_size": {"value": 16, "unit": "px"},
                    "font_weight": 999,  # Invalid
                    "line_height": {"value": 1.5, "unit": "em"},
                    "confidence": 0.5,
                }
            ]
        }
        schema = TypographyExtractionSchema.get_json_schema()
        with pytest.raises(JsonSchemaValidationError):
            validate(result, schema)


class TestShadowExtractionSchema:
    """Test shadow extraction schema."""

    def test_schema_name(self):
        """Schema should have correct name."""
        schema = ShadowExtractionSchema.get_tool_definition()
        assert schema["name"] == "extract_shadows"

    def test_schema_has_required_fields(self):
        """Schema should have all required fields for shadow tokens."""
        schema = ShadowExtractionSchema.get_tool_definition()
        input_schema = schema["input_schema"]
        properties = input_schema["properties"]["shadows"]["items"]["properties"]

        assert "name" in properties
        assert "offset_x" in properties
        assert "offset_y" in properties
        assert "blur_radius" in properties
        assert "spread_radius" in properties
        assert "color" in properties
        assert "confidence" in properties

    def test_valid_shadow_extraction_result(self):
        """Valid shadow extraction result should pass validation."""
        result = {
            "shadows": [
                {
                    "name": "shadow-md",
                    "offset_x": {"value": 0, "unit": "px"},
                    "offset_y": {"value": 4, "unit": "px"},
                    "blur_radius": {"value": 6, "unit": "px"},
                    "spread_radius": {"value": -1, "unit": "px"},
                    "color": "rgba(0, 0, 0, 0.1)",
                    "confidence": 0.85,
                    "type": "drop-shadow",
                    "usage": "Medium elevation shadow",
                }
            ]
        }
        schema = ShadowExtractionSchema.get_json_schema()
        validate(result, schema)


class TestGradientExtractionSchema:
    """Test gradient extraction schema."""

    def test_schema_name(self):
        """Schema should have correct name."""
        schema = GradientExtractionSchema.get_tool_definition()
        assert schema["name"] == "extract_gradients"

    def test_schema_has_required_fields(self):
        """Schema should have all required fields for gradient tokens."""
        schema = GradientExtractionSchema.get_tool_definition()
        input_schema = schema["input_schema"]
        properties = input_schema["properties"]["gradients"]["items"]["properties"]

        assert "name" in properties
        assert "type" in properties
        assert "stops" in properties
        assert "confidence" in properties

    def test_valid_gradient_extraction_result(self):
        """Valid gradient extraction result should pass validation."""
        result = {
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
                    "usage": "Primary gradient for buttons",
                }
            ]
        }
        schema = GradientExtractionSchema.get_json_schema()
        validate(result, schema)

    def test_invalid_gradient_type_fails(self):
        """Invalid gradient type should fail validation."""
        result = {
            "gradients": [
                {
                    "name": "test",
                    "type": "invalid-type",
                    "stops": [
                        {"color": "#FF0000", "position": 0},
                        {"color": "#0000FF", "position": 100},
                    ],
                    "confidence": 0.5,
                }
            ]
        }
        schema = GradientExtractionSchema.get_json_schema()
        with pytest.raises(JsonSchemaValidationError):
            validate(result, schema)


class TestValidateExtractionResult:
    """Test the validate_extraction_result function."""

    def test_validate_valid_result_returns_true(self):
        """Valid result should return True."""
        result = {"colors": [{"name": "test", "hex_value": "#FF0000", "confidence": 0.9}]}
        assert validate_extraction_result(TokenType.COLOR, result) is True

    def test_validate_invalid_result_raises_error(self):
        """Invalid result should raise validation error."""
        result = {
            "colors": [
                {
                    "name": "test",
                    # Missing required fields
                }
            ]
        }
        with pytest.raises(JsonSchemaValidationError):
            validate_extraction_result(TokenType.COLOR, result)

    def test_validate_all_token_types(self):
        """Validate function should work for all token types."""
        # This test ensures validate_extraction_result handles all types
        test_results = {
            TokenType.COLOR: {
                "colors": [{"name": "test", "hex_value": "#FF0000", "confidence": 0.9}]
            },
            TokenType.SPACING: {
                "spacing": [{"name": "test", "value": 8, "unit": "px", "confidence": 0.9}]
            },
            TokenType.TYPOGRAPHY: {
                "typography": [
                    {
                        "name": "test",
                        "font_family": "Arial",
                        "font_size": {"value": 16, "unit": "px"},
                        "font_weight": 400,
                        "line_height": {"value": 1.5, "unit": "em"},
                        "confidence": 0.9,
                    }
                ]
            },
            TokenType.SHADOW: {
                "shadows": [
                    {
                        "name": "test",
                        "offset_x": {"value": 0, "unit": "px"},
                        "offset_y": {"value": 4, "unit": "px"},
                        "blur_radius": {"value": 8, "unit": "px"},
                        "spread_radius": {"value": 0, "unit": "px"},
                        "color": "rgba(0, 0, 0, 0.1)",
                        "confidence": 0.9,
                    }
                ]
            },
            TokenType.GRADIENT: {
                "gradients": [
                    {
                        "name": "test",
                        "type": "linear",
                        "stops": [
                            {"color": "#FF0000", "position": 0},
                            {"color": "#0000FF", "position": 100},
                        ],
                        "confidence": 0.9,
                    }
                ]
            },
        }

        for token_type, result in test_results.items():
            assert validate_extraction_result(token_type, result) is True


class TestSchemaJsonSerializable:
    """Test that schemas are JSON serializable."""

    def test_all_schemas_json_serializable(self):
        """All schemas should be JSON serializable for API use."""
        for token_type in TokenType:
            schema = get_tool_schema(token_type)
            # Should not raise
            json_str = json.dumps(schema)
            assert json_str is not None
            # Should be able to parse back
            parsed = json.loads(json_str)
            assert parsed["name"] == schema["name"]
