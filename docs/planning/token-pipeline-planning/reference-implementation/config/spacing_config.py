"""
Spacing Token Pipeline Configuration

REFERENCE IMPLEMENTATION - This is planning/documentation code showing how the
spacing configuration should be structured when implemented. This code
is not meant to be run directly but serves as a complete reference for
implementing the actual configuration.

This module provides:
- SpacingConfig Pydantic Settings class
- All configurable parameters for the spacing pipeline
- Environment variable mappings with SPACING_ prefix
"""

from enum import Enum
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIProvider(str, Enum):
    """Supported AI providers for spacing extraction"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class SpacingConfig(BaseSettings):
    """
    Configuration for the spacing token extraction pipeline.

    All settings can be configured via environment variables with SPACING_ prefix.
    Example: SPACING_MAX_CONCURRENT_EXTRACTIONS=10
    """

    model_config = SettingsConfigDict(
        env_prefix="SPACING_",
        env_file=".env.spacing",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # AI Provider Configuration
    # ==========================================================================

    ai_provider: AIProvider = Field(
        default=AIProvider.ANTHROPIC,
        description="AI provider to use for spacing extraction (anthropic or openai)"
    )

    anthropic_model: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="Anthropic model for spacing extraction"
    )

    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model for spacing extraction"
    )

    # ==========================================================================
    # Extraction Settings
    # ==========================================================================

    default_max_spacing: int = Field(
        default=12,
        ge=1,
        le=50,
        description="Default maximum number of spacing values to extract per image"
    )

    max_concurrent_extractions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent API calls during batch extraction"
    )

    extraction_timeout_seconds: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Timeout for single image extraction"
    )

    retry_attempts: int = Field(
        default=3,
        ge=0,
        le=5,
        description="Number of retry attempts for failed extractions"
    )

    retry_delay_seconds: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between retry attempts in seconds"
    )

    # ==========================================================================
    # Aggregation Settings
    # ==========================================================================

    default_percentage_threshold: float = Field(
        default=0.10,
        ge=0.01,
        le=0.50,
        description="Default percentage threshold for deduplication (0.10 = 10%)"
    )

    # ==========================================================================
    # Base Unit Detection
    # ==========================================================================

    default_base_unit: int = Field(
        default=4,
        description="Default base unit for spacing (4px or 8px systems)"
    )

    prefer_8px_system: bool = Field(
        default=True,
        description="Prefer 8px base unit when values are divisible by both 4 and 8"
    )

    # ==========================================================================
    # REM Conversion
    # ==========================================================================

    default_rem_base: int = Field(
        default=16,
        ge=8,
        le=24,
        description="Base font size for rem calculations (typically 16px)"
    )

    # ==========================================================================
    # Scale Configuration
    # ==========================================================================

    scale_mapping: dict[int, str] = Field(
        default={
            0: "none",
            4: "2xs",
            8: "xs",
            12: "sm",
            16: "md",
            20: "md",
            24: "lg",
            32: "xl",
            40: "xl",
            48: "2xl",
            64: "3xl",
        },
        description="Mapping of pixel values to scale names"
    )

    # ==========================================================================
    # Responsive Scaling
    # ==========================================================================

    responsive_scale_mobile: float = Field(
        default=0.75,
        ge=0.5,
        le=1.0,
        description="Scale factor for mobile breakpoint"
    )

    responsive_scale_tablet: float = Field(
        default=1.0,
        ge=0.75,
        le=1.25,
        description="Scale factor for tablet breakpoint"
    )

    responsive_scale_desktop: float = Field(
        default=1.25,
        ge=1.0,
        le=2.0,
        description="Scale factor for desktop breakpoint"
    )

    responsive_scale_widescreen: float = Field(
        default=1.5,
        ge=1.0,
        le=2.5,
        description="Scale factor for widescreen breakpoint"
    )

    # ==========================================================================
    # Grid Compliance
    # ==========================================================================

    grid_compliance_bases: list[int] = Field(
        default=[4, 8],
        description="Base units to check for grid compliance"
    )

    # ==========================================================================
    # Confidence Settings
    # ==========================================================================

    default_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Default confidence when AI doesn't provide one"
    )

    min_confidence_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum confidence to include a spacing token"
    )

    # ==========================================================================
    # Streaming Settings
    # ==========================================================================

    streaming_enabled: bool = Field(
        default=True,
        description="Enable SSE streaming for real-time progress updates"
    )

    streaming_delay_ms: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Delay between SSE events in milliseconds"
    )

    # ==========================================================================
    # Caching Settings
    # ==========================================================================

    cache_enabled: bool = Field(
        default=True,
        description="Enable caching of extracted spacing tokens by image hash"
    )

    cache_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Cache time-to-live in seconds"
    )

    # ==========================================================================
    # Database Settings
    # ==========================================================================

    batch_insert_size: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Number of tokens to insert in a single database batch"
    )

    # ==========================================================================
    # Export Settings
    # ==========================================================================

    default_export_format: str = Field(
        default="w3c",
        description="Default export format (w3c, css, react, tailwind, scss)"
    )

    include_metadata_in_export: bool = Field(
        default=True,
        description="Include extraction metadata in exports"
    )

    # ==========================================================================
    # Logging Settings
    # ==========================================================================

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level for spacing pipeline"
    )

    log_extraction_details: bool = Field(
        default=False,
        description="Log detailed extraction information (verbose)"
    )

    # ==========================================================================
    # Validators
    # ==========================================================================

    @field_validator("default_percentage_threshold")
    @classmethod
    def validate_percentage_threshold(cls, v):
        """Ensure percentage threshold is reasonable"""
        if v < 0.01:
            raise ValueError("Percentage threshold must be at least 1%")
        if v > 0.50:
            raise ValueError("Percentage threshold must not exceed 50%")
        return v

    @field_validator("scale_mapping")
    @classmethod
    def validate_scale_mapping(cls, v):
        """Ensure scale mapping has required keys"""
        required_scales = ["xs", "sm", "md", "lg", "xl"]
        scales = set(v.values())
        for scale in required_scales:
            if scale not in scales:
                # Warning only - don't fail validation
                pass
        return v

    # ==========================================================================
    # Computed Properties
    # ==========================================================================

    @property
    def responsive_scales(self) -> dict[str, float]:
        """Get all responsive scale factors as a dict"""
        return {
            "mobile": self.responsive_scale_mobile,
            "tablet": self.responsive_scale_tablet,
            "desktop": self.responsive_scale_desktop,
            "widescreen": self.responsive_scale_widescreen,
        }

    @property
    def effective_model(self) -> str:
        """Get the model name based on selected AI provider"""
        if self.ai_provider == AIProvider.ANTHROPIC:
            return self.anthropic_model
        return self.openai_model


@lru_cache
def get_spacing_config() -> SpacingConfig:
    """
    Get cached spacing configuration instance.

    Uses lru_cache to ensure only one instance is created.
    """
    return SpacingConfig()


# =============================================================================
# Configuration Helpers
# =============================================================================

def get_scale_name(value_px: int, config: SpacingConfig | None = None) -> str:
    """
    Get scale name for a pixel value.

    Args:
        value_px: The pixel value
        config: Optional config instance (uses default if not provided)

    Returns:
        Scale name (e.g., "md", "lg")
    """
    if config is None:
        config = get_spacing_config()

    # Find closest match
    closest = min(
        config.scale_mapping.keys(),
        key=lambda x: abs(x - value_px)
    )
    return config.scale_mapping.get(closest, "custom")


def calculate_responsive_values(
    value_px: int,
    config: SpacingConfig | None = None
) -> dict[str, int]:
    """
    Calculate responsive values for all breakpoints.

    Args:
        value_px: Base pixel value
        config: Optional config instance

    Returns:
        Dict with mobile, tablet, desktop, widescreen values
    """
    if config is None:
        config = get_spacing_config()

    return {
        "mobile": int(value_px * config.responsive_scale_mobile),
        "tablet": int(value_px * config.responsive_scale_tablet),
        "desktop": int(value_px * config.responsive_scale_desktop),
        "widescreen": int(value_px * config.responsive_scale_widescreen),
    }


# =============================================================================
# Export Configuration for Different Formats
# =============================================================================

class ExportConfig(BaseSettings):
    """Configuration for spacing token exports"""

    model_config = SettingsConfigDict(
        env_prefix="SPACING_EXPORT_",
        extra="ignore",
    )

    # CSS Export
    css_variable_prefix: str = Field(
        default="spacing",
        description="Prefix for CSS custom properties"
    )

    css_include_rem: bool = Field(
        default=True,
        description="Include rem values in CSS export"
    )

    # W3C Export
    w3c_include_extensions: bool = Field(
        default=True,
        description="Include copy-that extensions in W3C export"
    )

    # React Export
    react_use_const: bool = Field(
        default=True,
        description="Use const assertion in React export"
    )

    react_include_types: bool = Field(
        default=True,
        description="Include TypeScript types in React export"
    )

    # Tailwind Export
    tailwind_extend_theme: bool = Field(
        default=True,
        description="Generate as theme extension rather than replacement"
    )


@lru_cache
def get_export_config() -> ExportConfig:
    """Get cached export configuration instance"""
    return ExportConfig()
