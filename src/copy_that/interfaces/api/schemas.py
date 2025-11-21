"""API schemas for request/response validation"""

from pydantic import BaseModel, ConfigDict, Field


# Project Schemas
class ProjectCreateRequest(BaseModel):
    """Request model for creating a project"""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, max_length=2000, description="Project description")

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdateRequest(BaseModel):
    """Request model for updating a project"""

    name: str | None = Field(None, min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, max_length=2000, description="Project description")

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """Response model for a project"""

    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: str | None = Field(None, description="Project description")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# Color Token Schemas
class ColorTokenResponse(BaseModel):
    """Comprehensive response model for a color token"""

    # Core display properties
    hex: str = Field(..., description="Hex color code")
    rgb: str = Field(..., description="RGB format")
    hsl: str | None = Field(None, description="HSL format")
    hsv: str | None = Field(None, description="HSV format")
    name: str = Field(..., description="Human-readable color name")

    # Design token properties
    design_intent: str | None = Field(
        None,
        description="DESIGN INTENT: Role Claude assigns to this color (e.g., primary, error, background)",
    )
    semantic_names: dict | None = Field(
        None,
        description="PERCEPTUAL ANALYSIS: 5-style color naming (simple/descriptive/emotional/technical/vibrancy) derived from color science",
    )
    category: str | None = Field(None, description="Color category")
    extraction_metadata: dict | None = Field(
        None,
        description="EXTRACTION SOURCE: Maps each attribute to the tool/function that extracted it (e.g., {'temperature': 'color_utils.get_color_temperature', 'design_intent': 'claude_ai_extractor'})",
    )

    # Color analysis properties
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    harmony: str | None = Field(None, description="Color harmony group")
    temperature: str | None = Field(None, description="Color temperature")
    saturation_level: str | None = Field(None, description="Saturation intensity")
    lightness_level: str | None = Field(None, description="Lightness level")
    usage: list[str] | None = Field(
        None, description="Usage contexts (e.g., backgrounds, text, accents)"
    )

    # Count & prominence
    count: int = Field(default=1, ge=1, description="Detection count")
    prominence_percentage: float | None = Field(
        None, ge=0, le=100, description="Image prominence %"
    )

    # Accessibility properties
    wcag_contrast_on_white: float | None = Field(None, description="Contrast ratio on white")
    wcag_contrast_on_black: float | None = Field(None, description="Contrast ratio on black")
    wcag_aa_compliant_text: bool | None = Field(None, description="WCAG AA text compliant")
    wcag_aaa_compliant_text: bool | None = Field(None, description="WCAG AAA text compliant")
    wcag_aa_compliant_normal: bool | None = Field(None, description="WCAG AA normal compliant")
    wcag_aaa_compliant_normal: bool | None = Field(None, description="WCAG AAA normal compliant")
    colorblind_safe: bool | None = Field(None, description="Safe for colorblind users")

    # Color variants
    tint_color: str | None = Field(None, description="Tint variant (50% lighter)")
    shade_color: str | None = Field(None, description="Shade variant (50% darker)")
    tone_color: str | None = Field(None, description="Tone variant (50% desaturated)")

    # Advanced properties
    closest_web_safe: str | None = Field(None, description="Closest web-safe color")
    closest_css_named: str | None = Field(None, description="Closest CSS named color")
    delta_e_to_dominant: float | None = Field(None, description="Delta E distance to dominant")
    is_neutral: bool | None = Field(None, description="Is neutral/grayscale")

    # ML/CV model properties
    kmeans_cluster_id: int | None = Field(None, description="K-means cluster ID")
    sam_segmentation_mask: str | None = Field(None, description="SAM segmentation mask")
    clip_embeddings: list[float] | None = Field(None, description="CLIP embeddings")
    histogram_significance: float | None = Field(
        None, ge=0, le=1, description="Histogram significance"
    )

    model_config = ConfigDict(from_attributes=True)


class ColorExtractionResponse(BaseModel):
    """Response model for color extraction"""

    colors: list[ColorTokenResponse] = Field(..., description="Extracted color tokens")
    dominant_colors: list[str] = Field(..., description="Top 3 dominant hex colors")
    color_palette: str = Field(..., description="Palette description")
    extraction_confidence: float = Field(..., ge=0, le=1, description="Overall confidence")

    model_config = ConfigDict(from_attributes=True)


class ExtractColorRequest(BaseModel):
    """Request model for color extraction from URL or base64"""

    image_url: str | None = Field(None, description="URL of image to analyze")
    image_base64: str | None = Field(None, description="Base64 encoded image data")
    project_id: int = Field(..., description="Project ID to associate colors with")
    max_colors: int = Field(10, ge=1, le=50, description="Maximum colors to extract")
    extractor: str | None = Field(
        "auto",
        description="Extractor to use: 'claude', 'openai', or 'auto' (uses OpenAI if available)",
    )

    model_config = ConfigDict(from_attributes=True)


class ColorTokenCreateRequest(BaseModel):
    """Request model for creating a color token"""

    project_id: int = Field(..., description="Project ID")
    extraction_job_id: int | None = Field(None, description="Extraction job ID")
    hex: str = Field(..., description="Hex color code")
    rgb: str = Field(..., description="RGB format")
    name: str = Field(..., description="Color name")
    design_intent: str | None = Field(None, description="Design intent role")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    harmony: str | None = Field(None, description="Color harmony")
    usage: str | None = Field(None, description="Usage as JSON")

    model_config = ConfigDict(from_attributes=True)


class ColorTokenDetailResponse(ColorTokenResponse):
    """Detailed response model for a color token with ID and metadata"""

    id: int = Field(..., description="Color token ID")
    project_id: int = Field(..., description="Project ID")
    extraction_job_id: int | None = Field(None, description="Extraction job ID")
    library_id: int | None = Field(None, description="Token library ID")
    role: str | None = Field(None, description="Token role (primary, secondary, accent, etc)")
    provenance: dict | None = Field(None, description="Image sources and confidence scores")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


# Session & Library Schemas
class SessionCreateRequest(BaseModel):
    """Request model for creating an extraction session"""

    project_id: int = Field(..., description="Project ID")
    name: str = Field(..., min_length=1, max_length=255, description="Session name")
    description: str | None = Field(None, max_length=2000, description="Session description")

    model_config = ConfigDict(from_attributes=True)


class SessionResponse(BaseModel):
    """Response model for an extraction session"""

    id: int = Field(..., description="Session ID")
    project_id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Session name")
    description: str | None = Field(None, description="Session description")
    image_count: int = Field(default=0, description="Number of images in session")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class BatchExtractRequest(BaseModel):
    """Request model for batch image extraction"""

    image_urls: list[str] = Field(
        ..., min_length=1, max_length=50, description="List of image URLs to extract"
    )
    max_colors: int = Field(10, ge=1, le=50, description="Maximum colors per image")

    model_config = ConfigDict(from_attributes=True)


class RoleAssignment(BaseModel):
    """Token role assignment"""

    token_id: int = Field(..., description="Color token ID")
    role: str = Field(
        ..., description="Role: primary, secondary, accent, neutral, success, warning, danger, info"
    )

    model_config = ConfigDict(from_attributes=True)


class CurateRequest(BaseModel):
    """Request model for token curation"""

    role_assignments: list[RoleAssignment] = Field(..., description="List of role assignments")
    notes: str | None = Field(None, description="Curation notes")

    model_config = ConfigDict(from_attributes=True)


class AggregatedTokenResponse(BaseModel):
    """Response model for aggregated color token"""

    hex: str = Field(..., description="Hex color code")
    rgb: str = Field(..., description="RGB format")
    name: str = Field(..., description="Color name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    role: str | None = Field(None, description="Token role")
    provenance: dict = Field(..., description="Source images and confidence scores")
    harmony: str | None = Field(None, description="Color harmony")
    temperature: str | None = Field(None, description="Color temperature")

    model_config = ConfigDict(from_attributes=True)


class LibraryStatistics(BaseModel):
    """Library statistics"""

    color_count: int = Field(..., description="Number of unique colors")
    image_count: int = Field(..., description="Number of source images")
    avg_confidence: float = Field(..., description="Average extraction confidence")
    min_confidence: float = Field(..., description="Minimum confidence")
    max_confidence: float = Field(..., description="Maximum confidence")
    dominant_colors: list[str] = Field(..., description="Top dominant colors")
    multi_image_colors: int = Field(..., description="Colors found in multiple images")

    model_config = ConfigDict(from_attributes=True)


class LibraryResponse(BaseModel):
    """Response model for token library"""

    id: int = Field(..., description="Library ID")
    session_id: int = Field(..., description="Session ID")
    token_type: str = Field(..., description="Token type (color, spacing, typography)")
    tokens: list[AggregatedTokenResponse] = Field(..., description="Aggregated tokens")
    statistics: LibraryStatistics = Field(..., description="Library statistics")
    is_curated: bool = Field(default=False, description="Whether library has been curated")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class ExportRequest(BaseModel):
    """Request model for token export"""

    format: str = Field(..., description="Export format: w3c, css, react, html")

    model_config = ConfigDict(from_attributes=True)


class ExportResponse(BaseModel):
    """Response model for export"""

    format: str = Field(..., description="Export format")
    content: str = Field(..., description="Exported content")
    mime_type: str = Field(..., description="MIME type of content")

    model_config = ConfigDict(from_attributes=True)
