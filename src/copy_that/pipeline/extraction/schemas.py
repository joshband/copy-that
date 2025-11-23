"""Tool Use schemas for token extraction.

Defines JSON Schema definitions for each token type used with Claude Tool Use.
Provides strict validation for extraction results.
"""

from typing import Any

from jsonschema import validate

from copy_that.pipeline import TokenType


class BaseExtractionSchema:
    """Base class for extraction schemas."""

    @classmethod
    def get_tool_definition(cls) -> dict[str, Any]:
        """Get Tool Use tool definition."""
        raise NotImplementedError

    @classmethod
    def get_json_schema(cls) -> dict[str, Any]:
        """Get JSON Schema for validation."""
        return cls.get_tool_definition()["input_schema"]


class ColorExtractionSchema(BaseExtractionSchema):
    """Schema for color token extraction."""

    @classmethod
    def get_tool_definition(cls) -> dict[str, Any]:
        """Get Tool Use tool definition for color extraction."""
        return {
            "name": "extract_colors",
            "description": "Extract color tokens from the design image. Identify all colors including brand colors, UI colors, and semantic colors.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "colors": {
                        "type": "array",
                        "description": "Array of extracted color tokens",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Token name (kebab-case, e.g., 'primary-blue')",
                                },
                                "hex_value": {
                                    "type": "string",
                                    "description": "Hex color value",
                                    "pattern": "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence score 0-1",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "rgb": {
                                    "type": "object",
                                    "description": "RGB color values",
                                    "properties": {
                                        "r": {"type": "integer", "minimum": 0, "maximum": 255},
                                        "g": {"type": "integer", "minimum": 0, "maximum": 255},
                                        "b": {"type": "integer", "minimum": 0, "maximum": 255},
                                    },
                                    "required": ["r", "g", "b"],
                                },
                                "hsl": {
                                    "type": "object",
                                    "description": "HSL color values",
                                    "properties": {
                                        "h": {"type": "number", "minimum": 0, "maximum": 360},
                                        "s": {"type": "number", "minimum": 0, "maximum": 100},
                                        "l": {"type": "number", "minimum": 0, "maximum": 100},
                                    },
                                    "required": ["h", "s", "l"],
                                },
                                "usage": {
                                    "type": "string",
                                    "description": "Recommended usage or context",
                                },
                                "category": {
                                    "type": "string",
                                    "description": "Color category",
                                    "enum": [
                                        "brand",
                                        "accent",
                                        "neutral",
                                        "semantic",
                                        "background",
                                        "text",
                                        "border",
                                    ],
                                },
                            },
                            "required": ["name", "hex_value", "confidence"],
                        },
                    }
                },
                "required": ["colors"],
            },
        }


class SpacingExtractionSchema(BaseExtractionSchema):
    """Schema for spacing token extraction."""

    @classmethod
    def get_tool_definition(cls) -> dict[str, Any]:
        """Get Tool Use tool definition for spacing extraction."""
        return {
            "name": "extract_spacing",
            "description": "Extract spacing tokens from the design image. Identify consistent spacing patterns and scale.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "spacing": {
                        "type": "array",
                        "description": "Array of extracted spacing tokens",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Token name (e.g., 'space-sm', 'space-md')",
                                },
                                "value": {"type": "number", "description": "Numeric value"},
                                "unit": {
                                    "type": "string",
                                    "description": "Unit of measurement",
                                    "enum": ["px", "rem", "em", "%"],
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence score 0-1",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "usage": {
                                    "type": "string",
                                    "description": "Recommended usage context",
                                },
                                "scale_position": {
                                    "type": "integer",
                                    "description": "Position in spacing scale (1=smallest)",
                                    "minimum": 1,
                                },
                            },
                            "required": ["name", "value", "unit", "confidence"],
                        },
                    }
                },
                "required": ["spacing"],
            },
        }


class TypographyExtractionSchema(BaseExtractionSchema):
    """Schema for typography token extraction."""

    @classmethod
    def get_tool_definition(cls) -> dict[str, Any]:
        """Get Tool Use tool definition for typography extraction."""
        return {
            "name": "extract_typography",
            "description": "Extract typography tokens from the design image. Identify font families, sizes, weights, and text styles.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "typography": {
                        "type": "array",
                        "description": "Array of extracted typography tokens",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Token name (e.g., 'heading-1', 'body-text')",
                                },
                                "font_family": {
                                    "type": "string",
                                    "description": "Font family name",
                                },
                                "font_size": {
                                    "type": "object",
                                    "description": "Font size with unit",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "unit": {
                                            "type": "string",
                                            "enum": ["px", "rem", "em", "pt"],
                                        },
                                    },
                                    "required": ["value", "unit"],
                                },
                                "font_weight": {
                                    "type": "integer",
                                    "description": "Font weight (100-900)",
                                    "minimum": 100,
                                    "maximum": 900,
                                    "multipleOf": 100,
                                },
                                "line_height": {
                                    "type": "object",
                                    "description": "Line height with unit",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "unit": {
                                            "type": "string",
                                            "enum": ["px", "em", "%", "unitless"],
                                        },
                                    },
                                    "required": ["value", "unit"],
                                },
                                "letter_spacing": {
                                    "type": "object",
                                    "description": "Letter spacing with unit",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "unit": {"type": "string", "enum": ["px", "em", "%"]},
                                    },
                                    "required": ["value", "unit"],
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence score 0-1",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "usage": {
                                    "type": "string",
                                    "description": "Recommended usage context",
                                },
                            },
                            "required": [
                                "name",
                                "font_family",
                                "font_size",
                                "font_weight",
                                "line_height",
                                "confidence",
                            ],
                        },
                    }
                },
                "required": ["typography"],
            },
        }


class ShadowExtractionSchema(BaseExtractionSchema):
    """Schema for shadow token extraction."""

    @classmethod
    def get_tool_definition(cls) -> dict[str, Any]:
        """Get Tool Use tool definition for shadow extraction."""
        return {
            "name": "extract_shadows",
            "description": "Extract shadow tokens from the design image. Identify drop shadows, box shadows, and elevation patterns.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "shadows": {
                        "type": "array",
                        "description": "Array of extracted shadow tokens",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Token name (e.g., 'shadow-sm', 'shadow-md')",
                                },
                                "offset_x": {
                                    "type": "object",
                                    "description": "Horizontal offset",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "unit": {"type": "string", "enum": ["px", "rem", "em"]},
                                    },
                                    "required": ["value", "unit"],
                                },
                                "offset_y": {
                                    "type": "object",
                                    "description": "Vertical offset",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "unit": {"type": "string", "enum": ["px", "rem", "em"]},
                                    },
                                    "required": ["value", "unit"],
                                },
                                "blur_radius": {
                                    "type": "object",
                                    "description": "Blur radius",
                                    "properties": {
                                        "value": {"type": "number", "minimum": 0},
                                        "unit": {"type": "string", "enum": ["px", "rem", "em"]},
                                    },
                                    "required": ["value", "unit"],
                                },
                                "spread_radius": {
                                    "type": "object",
                                    "description": "Spread radius",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "unit": {"type": "string", "enum": ["px", "rem", "em"]},
                                    },
                                    "required": ["value", "unit"],
                                },
                                "color": {
                                    "type": "string",
                                    "description": "Shadow color (hex or rgba)",
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence score 0-1",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "type": {
                                    "type": "string",
                                    "description": "Shadow type",
                                    "enum": ["drop-shadow", "box-shadow", "inner-shadow"],
                                },
                                "usage": {
                                    "type": "string",
                                    "description": "Recommended usage context",
                                },
                            },
                            "required": [
                                "name",
                                "offset_x",
                                "offset_y",
                                "blur_radius",
                                "spread_radius",
                                "color",
                                "confidence",
                            ],
                        },
                    }
                },
                "required": ["shadows"],
            },
        }


class GradientExtractionSchema(BaseExtractionSchema):
    """Schema for gradient token extraction."""

    @classmethod
    def get_tool_definition(cls) -> dict[str, Any]:
        """Get Tool Use tool definition for gradient extraction."""
        return {
            "name": "extract_gradients",
            "description": "Extract gradient tokens from the design image. Identify linear, radial, and conic gradients.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "gradients": {
                        "type": "array",
                        "description": "Array of extracted gradient tokens",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Token name (e.g., 'gradient-primary')",
                                },
                                "type": {
                                    "type": "string",
                                    "description": "Gradient type",
                                    "enum": ["linear", "radial", "conic"],
                                },
                                "angle": {
                                    "type": "number",
                                    "description": "Angle in degrees (for linear gradients)",
                                    "minimum": 0,
                                    "maximum": 360,
                                },
                                "stops": {
                                    "type": "array",
                                    "description": "Color stops",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "color": {
                                                "type": "string",
                                                "description": "Color value (hex or rgba)",
                                            },
                                            "position": {
                                                "type": "number",
                                                "description": "Stop position (0-100%)",
                                                "minimum": 0,
                                                "maximum": 100,
                                            },
                                        },
                                        "required": ["color", "position"],
                                    },
                                    "minItems": 2,
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence score 0-1",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "usage": {
                                    "type": "string",
                                    "description": "Recommended usage context",
                                },
                            },
                            "required": ["name", "type", "stops", "confidence"],
                        },
                    }
                },
                "required": ["gradients"],
            },
        }


# Schema registry mapping token types to schema classes
SCHEMA_REGISTRY: dict[TokenType, type[BaseExtractionSchema]] = {
    TokenType.COLOR: ColorExtractionSchema,
    TokenType.SPACING: SpacingExtractionSchema,
    TokenType.TYPOGRAPHY: TypographyExtractionSchema,
    TokenType.SHADOW: ShadowExtractionSchema,
    TokenType.GRADIENT: GradientExtractionSchema,
}


def get_tool_schema(token_type: TokenType | str) -> dict[str, Any]:
    """Get Tool Use tool definition for a token type.

    Args:
        token_type: Token type (enum or string)

    Returns:
        Tool definition dictionary

    Raises:
        KeyError: If token type is not in registry
    """
    if isinstance(token_type, str):
        token_type = TokenType(token_type)

    if token_type not in SCHEMA_REGISTRY:
        raise KeyError(f"No schema registered for token type: {token_type}")

    return SCHEMA_REGISTRY[token_type].get_tool_definition()


def get_all_schemas() -> list[dict[str, Any]]:
    """Get all Tool Use tool definitions.

    Returns:
        List of all tool definitions
    """
    return [schema_class.get_tool_definition() for schema_class in SCHEMA_REGISTRY.values()]


def validate_extraction_result(token_type: TokenType | str, result: dict[str, Any]) -> bool:
    """Validate extraction result against schema.

    Args:
        token_type: Token type for validation
        result: Extraction result to validate

    Returns:
        True if valid

    Raises:
        JsonSchemaValidationError: If validation fails
    """
    if isinstance(token_type, str):
        token_type = TokenType(token_type)

    schema = SCHEMA_REGISTRY[token_type].get_json_schema()
    validate(result, schema)
    return True
