"""
Mood Board API - AI-curated aesthetic boards based on extracted color tokens

Uses Claude Sonnet 4.5 for content generation and OpenAI DALL-E for image generation
"""

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/mood-board",
    tags=["mood-board"],
    responses={404: {"description": "Not found"}},
)


class ColorInput(BaseModel):
    """Simplified color token for mood board generation"""

    hex: str
    name: str | None = None
    temperature: Literal["warm", "cool", "neutral"] | None = None
    saturation_level: Literal["vibrant", "muted", "desaturated", "grayscale"] | None = None
    hue_family: str | None = None


class VisualElement(BaseModel):
    """Visual element description"""

    type: Literal["texture", "shape", "pattern", "object", "composition"]
    description: str
    prominence: Literal["primary", "secondary", "accent"]


class AestheticReference(BaseModel):
    """Cultural/artistic reference"""

    movement: str
    artist: str | None = None
    period: str | None = None
    characteristics: list[str] = Field(default_factory=list)


class GeneratedImage(BaseModel):
    """AI-generated image data"""

    url: str
    prompt: str
    revised_prompt: str | None = None


class MoodBoardTheme(BaseModel):
    """Complete mood board theme"""

    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    visual_elements: list[VisualElement] = Field(default_factory=list)
    color_palette: list[str] = Field(default_factory=list)
    references: list[AestheticReference] = Field(default_factory=list)
    generated_images: list[GeneratedImage] = Field(default_factory=list)


class MoodBoardVariant(BaseModel):
    """Complete mood board variant"""

    id: str
    title: str
    subtitle: str
    theme: MoodBoardTheme
    dominant_colors: list[str] = Field(default_factory=list)
    vibe: str


class MoodBoardRequest(BaseModel):
    """Request to generate mood board"""

    colors: list[ColorInput] = Field(..., min_length=1, max_length=20)
    num_variants: int = Field(default=2, ge=1, le=3)
    include_images: bool = Field(default=True)
    num_images_per_variant: int = Field(default=4, ge=1, le=6)
    focus_type: Literal["material", "typography"] = Field(default="material")


class MoodBoardResponse(BaseModel):
    """Response with generated mood boards"""

    variants: list[MoodBoardVariant]
    generation_time_ms: float
    models_used: dict[str, str]
    focus_type: str


@router.post("/generate", response_model=MoodBoardResponse)
async def generate_mood_board(request: MoodBoardRequest):
    """
    Generate AI-curated mood boards based on color tokens

    Uses:
    - Claude Sonnet 4.5 for thematic content generation
    - OpenAI DALL-E 3 for visual image generation

    Returns 1-3 mood board variants with themes, references, and generated images
    """
    try:
        # Import the generator service
        from copy_that.services.mood_board_generator import MoodBoardGenerator

        generator = MoodBoardGenerator()

        # Generate mood boards
        result = await generator.generate(
            colors=request.colors,
            num_variants=request.num_variants,
            include_images=request.include_images,
            num_images_per_variant=request.num_images_per_variant,
            focus_type=request.focus_type,
        )

        return result

    except ImportError as e:
        logger.error(f"Failed to import MoodBoardGenerator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Mood board generator not available. Check server configuration.",
        )
    except Exception as e:
        logger.error(f"Error generating mood board: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate mood board: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """Health check for mood board service"""
    import os

    return {
        "status": "healthy",
        "anthropic_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }
