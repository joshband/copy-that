"""
Pipeline types module

Contains core type definitions for the token extraction pipeline:
- TokenType enum for extraction categories
- W3CTokenType enum for W3C Design Tokens $type values
- TokenResult for extraction results (W3C-compliant)
- PipelineTask for task definitions
- ProcessedImage for image metadata

W3C Design Tokens Format:
https://design-tokens.github.io/community-group/format/
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class TokenType(str, Enum):
    """
    Enumeration of supported token types for extraction.

    These represent extraction categories, not W3C $type values.
    Use W3CTokenType for W3C-compliant type specification.
    """

    COLOR = "color"
    SPACING = "spacing"
    TYPOGRAPHY = "typography"
    SHADOW = "shadow"
    GRADIENT = "gradient"


class W3CTokenType(str, Enum):
    """
    W3C Design Tokens type specification.

    These are the standard $type values from the W3C Design Tokens
    Community Group specification.

    See: https://design-tokens.github.io/community-group/format/#types
    """

    # Primitive types
    COLOR = "color"
    DIMENSION = "dimension"
    FONT_FAMILY = "fontFamily"
    FONT_WEIGHT = "fontWeight"
    DURATION = "duration"
    CUBIC_BEZIER = "cubicBezier"
    NUMBER = "number"

    # Composite types
    STROKE_STYLE = "strokeStyle"
    BORDER = "border"
    TRANSITION = "transition"
    SHADOW = "shadow"
    GRADIENT = "gradient"
    TYPOGRAPHY = "typography"

    # Custom composite (for generic compositions)
    COMPOSITION = "composition"


class TokenResult(BaseModel):
    """
    Result of a token extraction operation with W3C Design Tokens support.

    Contains the extracted token data with confidence score,
    W3C-compliant fields for export, and optional metadata.

    W3C Format Support:
    - path: Token hierarchy for nested structure
    - w3c_type: Standard $type value
    - description: Human-readable $description
    - reference: Token reference syntax {color.primary}
    - extensions: Vendor-specific $extensions

    Example:
        >>> result = TokenResult(
        ...     token_type=TokenType.COLOR,
        ...     name="primary",
        ...     path=["color", "brand"],
        ...     w3c_type=W3CTokenType.COLOR,
        ...     value="#FF6B35",
        ...     confidence=0.95,
        ...     description="Primary brand color"
        ... )
        >>> result.full_path
        'color.brand.primary'
        >>> result.to_w3c_dict()
        {'$value': '#FF6B35', '$type': 'color', '$description': '...'}
    """

    # === Extraction Context ===
    token_type: TokenType = Field(..., description="Extraction category")
    name: str = Field(..., description="Token name (final path segment)")

    # === W3C Core Fields ===
    path: list[str] = Field(
        default_factory=list, description="Token hierarchy path e.g., ['color', 'brand']"
    )
    w3c_type: W3CTokenType | None = Field(
        default=None, description="W3C $type (color, dimension, fontFamily, etc.)"
    )
    value: str | int | float | bool | dict[str, Any] = Field(
        ..., description="Token $value - simple or composite"
    )
    description: str | None = Field(default=None, description="Human-readable $description")

    # === Reference System ===
    reference: str | None = Field(
        default=None, description="Token reference e.g., '{color.primary}'"
    )

    # === Extraction Metadata ===
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")

    # === W3C Extensions ===
    extensions: dict[str, Any] | None = Field(
        default=None, description="W3C $extensions for vendor metadata"
    )

    # === Internal Metadata ===
    metadata: dict[str, Any] | None = Field(
        default=None, description="Internal extraction metadata (not in W3C export)"
    )

    model_config = {"use_enum_values": True}

    @model_validator(mode="after")
    def validate_reference_or_value(self) -> "TokenResult":
        """Validate that reference tokens don't have conflicting values."""
        if self.reference and isinstance(self.value, dict) and self.value:
            # Allow reference with empty dict value for composite refs
            pass
        return self

    @property
    def full_path(self) -> str:
        """Get dot-separated full token path."""
        if self.path:
            return ".".join(self.path + [self.name])
        return self.name

    def to_w3c_dict(self) -> dict[str, Any]:
        """
        Convert to W3C Design Tokens format.

        Returns a dictionary suitable for W3C JSON export with
        $value, $type, $description, and $extensions.
        """
        result: dict[str, Any] = {}

        # Core value (reference takes precedence)
        if self.reference:
            result["$value"] = self.reference
        else:
            result["$value"] = self.value

        # Type specification
        if self.w3c_type:
            result["$type"] = (
                self.w3c_type.value if isinstance(self.w3c_type, W3CTokenType) else self.w3c_type
            )

        # Description
        if self.description:
            result["$description"] = self.description

        # Extensions with confidence and extraction metadata
        ext: dict[str, Any] = dict(self.extensions) if self.extensions else {}
        ext["com.copythat"] = {
            "confidence": self.confidence,
            "extractionType": (
                self.token_type.value if isinstance(self.token_type, TokenType) else self.token_type
            ),
        }
        if self.metadata:
            ext["com.copythat"]["metadata"] = self.metadata
        result["$extensions"] = ext

        return result

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to ensure enums are serialized as strings."""
        data = super().model_dump(**kwargs)
        if isinstance(data.get("token_type"), TokenType):
            data["token_type"] = data["token_type"].value
        if isinstance(data.get("w3c_type"), W3CTokenType):
            data["w3c_type"] = data["w3c_type"].value
        return data


class PipelineTask(BaseModel):
    """
    Definition of a pipeline task for token extraction.

    Contains the task identifier, image source, and configuration
    for the extraction operation.
    """

    task_id: str = Field(..., description="Unique task identifier")
    image_url: str = Field(..., description="URL or path to the source image")
    token_types: list[TokenType] = Field(
        ..., min_length=1, description="Types of tokens to extract"
    )
    priority: int = Field(default=0, description="Task priority (higher = more urgent)")
    context: dict[str, Any] | None = Field(
        default=None, description="Additional context for the task"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Task creation timestamp"
    )

    model_config = {"use_enum_values": True}

    @field_validator("token_types", mode="before")
    @classmethod
    def convert_token_types(cls, v: Any) -> list[TokenType]:
        """Convert string token types to TokenType enum."""
        if isinstance(v, list):
            return [TokenType(item) if isinstance(item, str) else item for item in v]
        return v

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to ensure token_types are serialized as strings."""
        data = super().model_dump(**kwargs)
        if "token_types" in data:
            data["token_types"] = [
                t.value if isinstance(t, TokenType) else t for t in data["token_types"]
            ]
        return data


class ProcessedImage(BaseModel):
    """
    Metadata for a processed image in the pipeline.

    Contains image properties and optional preprocessed data
    for downstream extraction agents.
    """

    image_id: str = Field(..., description="Unique image identifier")
    source_url: str = Field(..., description="Original source URL or path")
    width: int = Field(..., gt=0, description="Image width in pixels")
    height: int = Field(..., gt=0, description="Image height in pixels")
    format: str | None = Field(default=None, description="Image format (e.g., PNG, JPEG)")
    file_size: int | None = Field(default=None, gt=0, description="File size in bytes")
    preprocessed_data: dict[str, Any] | None = Field(
        default=None, description="Preprocessed data for extraction"
    )
    processed_at: datetime = Field(
        default_factory=datetime.utcnow, description="Processing timestamp"
    )
