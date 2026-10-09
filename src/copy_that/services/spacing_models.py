"""Transport-neutral spacing extraction request and result contracts."""

from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from copy_that.services.artifact_models import ArtifactBundle


class SpacingExtractionRequest(BaseModel):
    """Request model for single image spacing extraction."""

    image_url: HttpUrl | None = Field(None, description="URL of the image to analyze")
    image_base64: str | None = Field(
        None, description="Base64 image payload (data URL payload without the prefix)"
    )
    image_media_type: str | None = Field(
        "image/png", description="Media type for base64 image (e.g., image/png)"
    )
    expected_base_px: int | None = Field(
        default=None,
        ge=1,
        le=128,
        description="Optional expected base spacing (px) for cross-check",
    )
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_tokens: int = Field(
        default=15, ge=1, le=50, description="Maximum spacing tokens to extract"
    )
    quality: str = Field("standard", description="Extraction quality: fast|standard|premium")
    use_multi_extractor: bool = Field(
        default=False,
        description="When true, use SpacingExtractionOrchestrator (CV+AI parallel)",
    )


class BatchSpacingExtractionRequest(BaseModel):
    """Request model for batch spacing extraction."""

    image_urls: list[HttpUrl] = Field(
        ..., min_length=1, max_length=20, description="List of image URLs"
    )
    max_tokens: int = Field(default=15, ge=1, le=50, description="Max tokens per image")
    similarity_threshold: float = Field(
        default=10.0, ge=1.0, le=50.0, description="Percentage threshold for deduplication"
    )


class SpacingTokenResponse(BaseModel):
    """Response model for a single spacing token."""

    value_px: int
    value_rem: float
    name: str
    confidence: float
    semantic_role: str | None = None
    spacing_type: str | None = None
    role: str | None = None
    grid_aligned: bool | None = None
    tailwind_class: str | None = None


class SpacingCommonValue(BaseModel):
    """Aggregated spacing diagnostic for adjacent elements."""

    value_px: int
    count: int
    orientation: str = Field(
        "mixed", description="Dominant direction for the spacing (horizontal|vertical|mixed)"
    )


class SpacingExtractionResponse(BaseModel):
    """Response model for spacing extraction result."""

    tokens: list[SpacingTokenResponse]
    scale_system: str
    base_unit: int
    grid_compliance: float
    extraction_confidence: float
    unique_values: list[int]
    min_spacing: int
    max_spacing: int
    cv_gap_diagnostics: dict | None = None
    base_alignment: dict | None = None
    cv_gaps_sample: list[float] | None = None
    cv_distance_candidates: list[dict[str, Any]] | None = None
    design_tokens: dict[str, Any] | None = None
    artifacts: ArtifactBundle | None = None
    baseline_spacing: dict | None = None
    component_spacing_metrics: list[dict[str, Any]] | None = None
    grid_detection: dict | None = None
    debug_overlay: str | None = None
    common_spacings: list[SpacingCommonValue] | None = None
    warnings: list[str] | None = None
    spacing_confidence_breakdown: dict[str, float] | None = None
    alignment: dict | None = None
    gap_clusters: dict | None = None
    token_graph: list[dict[str, Any]] | None = None
    fastsam_regions: list[dict[str, Any]] | None = None
    fastsam_tokens: list[dict[str, Any]] | None = None
    text_tokens: list[dict[str, Any]] | None = None
    uied_tokens: list[dict[str, Any]] | None = None
    elevation_tokens: list[dict[str, Any]] | None = None
    extractor_used: str | None = Field(
        default=None, description="Extractor path used (e.g. multi-extractor-orchestrator)"
    )
    failed_extractors: list[dict[str, str]] | None = Field(
        default=None, description="Extractors that failed during multi-extractor runs"
    )


class BatchExtractionResponse(BaseModel):
    """Response model for batch extraction result."""

    tokens: list[SpacingTokenResponse]
    statistics: dict
    library_id: str | None = None
    design_tokens: dict[str, Any] | None = None
