"""
Pipeline types module

Contains core type definitions for the token extraction pipeline:
- TokenType enum for different token categories
- TokenResult for extraction results
- PipelineTask for task definitions
- ProcessedImage for image metadata
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TokenType(str, Enum):
    """Enumeration of supported token types for extraction."""

    COLOR = "color"
    SPACING = "spacing"
    TYPOGRAPHY = "typography"
    SHADOW = "shadow"
    GRADIENT = "gradient"


class TokenResult(BaseModel):
    """
    Result of a token extraction operation.

    Contains the extracted token data with confidence score
    and optional metadata from the extraction process.
    """

    token_type: TokenType = Field(..., description="Type of token extracted")
    name: str = Field(..., description="Semantic name for the token")
    value: str = Field(..., description="Token value (e.g., hex color, dimension)")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score between 0 and 1"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata from extraction"
    )

    model_config = {"use_enum_values": True}

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to ensure token_type is serialized as string."""
        data = super().model_dump(**kwargs)
        if isinstance(data.get("token_type"), TokenType):
            data["token_type"] = data["token_type"].value
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
    file_size: int | None = Field(
        default=None, gt=0, description="File size in bytes"
    )
    preprocessed_data: dict[str, Any] | None = Field(
        default=None, description="Preprocessed data for extraction"
    )
    processed_at: datetime = Field(
        default_factory=datetime.utcnow, description="Processing timestamp"
    )
