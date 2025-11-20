"""API schemas for request/response validation"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Project Schemas
class ProjectCreateRequest(BaseModel):
    """Request model for creating a project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdateRequest(BaseModel):
    """Request model for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """Response model for a project"""
    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# Color Token Schemas
class ColorTokenResponse(BaseModel):
    """Response model for a color token"""
    hex: str = Field(..., description="Hex color code")
    rgb: str = Field(..., description="RGB format")
    name: str = Field(..., description="Human-readable color name")
    semantic_name: Optional[str] = Field(None, description="Semantic token name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    harmony: Optional[str] = Field(None, description="Color harmony group")
    usage: list[str] = Field(default_factory=list, description="Usage contexts")

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
    image_url: Optional[str] = Field(None, description="URL of image to analyze")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data")
    project_id: int = Field(..., description="Project ID to associate colors with")
    max_colors: int = Field(10, ge=1, le=50, description="Maximum colors to extract")

    model_config = ConfigDict(from_attributes=True)


class ColorTokenCreateRequest(BaseModel):
    """Request model for creating a color token"""
    project_id: int = Field(..., description="Project ID")
    extraction_job_id: Optional[int] = Field(None, description="Extraction job ID")
    hex: str = Field(..., description="Hex color code")
    rgb: str = Field(..., description="RGB format")
    name: str = Field(..., description="Color name")
    semantic_name: Optional[str] = Field(None, description="Semantic token name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    harmony: Optional[str] = Field(None, description="Color harmony")
    usage: Optional[str] = Field(None, description="Usage as JSON")

    model_config = ConfigDict(from_attributes=True)


class ColorTokenDetailResponse(BaseModel):
    """Detailed response model for a color token with ID"""
    id: int = Field(..., description="Color token ID")
    project_id: int = Field(..., description="Project ID")
    extraction_job_id: Optional[int] = Field(None, description="Extraction job ID")
    hex: str = Field(..., description="Hex color code")
    rgb: str = Field(..., description="RGB format")
    name: str = Field(..., description="Color name")
    semantic_name: Optional[str] = Field(None, description="Semantic token name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    harmony: Optional[str] = Field(None, description="Color harmony")
    usage: Optional[str] = Field(None, description="Usage contexts")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)
