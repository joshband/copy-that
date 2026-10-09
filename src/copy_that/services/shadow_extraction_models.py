"""Transport-neutral request and result models for shadow extraction."""

from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from copy_that.services.artifact_models import ArtifactBundle


class ShadowTokenResponse(BaseModel):
    """Response model for a single shadow token."""

    x_offset: float = Field(..., description="X offset in pixels")
    y_offset: float = Field(..., description="Y offset in pixels")
    blur_radius: float = Field(..., description="Blur radius in pixels")
    spread_radius: float = Field(default=0.0, description="Spread radius in pixels")
    color_hex: str = Field(..., description="Shadow color in hex format")
    opacity: float = Field(..., ge=0, le=1, description="Opacity (0-1)")
    name: str = Field(..., description="Shadow token name")
    shadow_type: str | None = Field(None, description="Shadow type (drop, inner, text)")
    semantic_role: str | None = Field(None, description="Semantic role (subtle, medium, strong)")
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")


class ShadowExtractionRequest(BaseModel):
    """Request model for shadow extraction."""

    image_url: HttpUrl | None = Field(None, description="URL of the image to analyze")
    image_base64: str | None = Field(
        None, description="Base64 image payload (data URL payload without the prefix)"
    )
    image_media_type: str | None = Field(
        "image/png", description="Media type for base64 image (e.g., image/png)"
    )
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_tokens: int = Field(default=10, ge=1, le=50, description="Maximum shadow tokens to extract")
    quality: str = Field("standard", description="Extraction quality: fast|standard|premium")
    include_artifacts: bool = Field(
        default=False, description="Include shadowlab artifact previews"
    )
    use_multi_extractor: bool = Field(
        default=False,
        description="When true, use ShadowExtractionOrchestrator (CV+AI parallel)",
    )


class ShadowExtractionResponse(BaseModel):
    """Response model for shadow extraction result."""

    tokens: list[ShadowTokenResponse] = Field(..., description="Extracted shadow tokens")
    extraction_confidence: float = Field(
        ..., ge=0, le=1, description="Overall extraction confidence"
    )
    extraction_metadata: dict[str, Any] | None = Field(
        None, description="Extraction metadata and diagnostics"
    )
    artifacts: ArtifactBundle | None = Field(None, description="Shadow extraction artifacts")
    warnings: list[str] | None = Field(None, description="Any warnings during extraction")
    extractor_used: str | None = Field(
        default=None, description="Extractor path used (e.g. multi-extractor-orchestrator)"
    )
    failed_extractors: list[dict[str, str]] | None = Field(
        default=None, description="Extractors that failed during multi-extractor runs"
    )


class ShadowBatchRequest(BaseModel):
    """Batch shadow extraction request."""

    image_urls: list[HttpUrl] = Field(..., min_length=1, description="Image URLs to analyze")
    project_id: int | None = Field(None, description="Optional project for persistence")
    max_tokens: int = Field(default=10, ge=1, le=50, description="Maximum shadow tokens per image")


class ShadowBatchItemResponse(BaseModel):
    """Per-image batch extraction result."""

    image_url: HttpUrl
    tokens: list[ShadowTokenResponse]
    extractor_used: str
    extraction_confidence: float
    warnings: list[str] | None = None


class ShadowBatchResponse(BaseModel):
    """Batch response."""

    results: list[ShadowBatchItemResponse]
