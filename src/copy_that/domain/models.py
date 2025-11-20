"""
Domain models for Copy That platform
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from copy_that.infrastructure.database import Base


class Project(Base):
    """A project containing design token extractions"""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"


class ExtractionJob(Base):
    """An extraction job for processing images/videos/audio"""
    __tablename__ = "extraction_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False)
    extraction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'color', 'spacing', 'typography', 'all'
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False
    )  # 'pending', 'processing', 'completed', 'failed'
    result_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<ExtractionJob(id={self.id}, type='{self.extraction_type}', status='{self.status}')>"


class ColorToken(Base):
    """Comprehensive color token with properties for all ML models/techniques"""
    __tablename__ = "color_tokens"

    # Core identifiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    extraction_job_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Core display properties
    hex: Mapped[str] = mapped_column(String(7), nullable=False)
    rgb: Mapped[str] = mapped_column(String(20), nullable=False)
    hsl: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    hsv: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Design token properties
    semantic_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Color analysis properties
    confidence: Mapped[float] = mapped_column(nullable=False)
    harmony: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    temperature: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    saturation_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    lightness_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    usage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Count & prominence
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    prominence_percentage: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Accessibility properties
    wcag_contrast_on_white: Mapped[Optional[float]] = mapped_column(nullable=True)
    wcag_contrast_on_black: Mapped[Optional[float]] = mapped_column(nullable=True)
    wcag_aa_compliant_text: Mapped[Optional[bool]] = mapped_column(nullable=True)
    wcag_aaa_compliant_text: Mapped[Optional[bool]] = mapped_column(nullable=True)
    wcag_aa_compliant_normal: Mapped[Optional[bool]] = mapped_column(nullable=True)
    wcag_aaa_compliant_normal: Mapped[Optional[bool]] = mapped_column(nullable=True)
    colorblind_safe: Mapped[Optional[bool]] = mapped_column(nullable=True)

    # Color variants
    tint_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    shade_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    tone_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)

    # Advanced properties
    closest_web_safe: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    closest_css_named: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    delta_e_to_dominant: Mapped[Optional[float]] = mapped_column(nullable=True)
    is_neutral: Mapped[Optional[bool]] = mapped_column(nullable=True)

    # ML/CV model properties
    kmeans_cluster_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sam_segmentation_mask: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clip_embeddings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    histogram_significance: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<ColorToken(id={self.id}, hex='{self.hex}', name='{self.name}', semantic='{self.semantic_name}')>"
