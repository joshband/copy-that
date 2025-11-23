"""
Domain models for Copy That platform
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from copy_that.infrastructure.database import Base


def utc_now() -> datetime:
    """Return current UTC time as naive datetime (for TIMESTAMP WITHOUT TIME ZONE)"""
    return datetime.now(UTC).replace(tzinfo=None)


class User(Base):
    """User account model"""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Roles (stored as JSON string)
    roles: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array: ["user", "admin"]

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class APIKey(Base):
    """API key for programmatic access"""

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(8), nullable=False)

    # Permissions (stored as JSON string)
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array: ["read", "write"]

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name='{self.name}', prefix='{self.key_prefix}')>"


class Project(Base):
    """A project containing design token extractions"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    owner: Mapped["User | None"] = relationship(back_populates="projects")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"


class ExtractionJob(Base):
    """An extraction job for processing images/videos/audio"""

    __tablename__ = "extraction_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False)
    extraction_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'color', 'spacing', 'typography', 'all'
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # 'pending', 'processing', 'completed', 'failed'
    result_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<ExtractionJob(id={self.id}, type='{self.extraction_type}', status='{self.status}')>"
        )


class ColorToken(Base):
    """Comprehensive color token with properties for all ML models/techniques"""

    __tablename__ = "color_tokens"

    # Core identifiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False)
    extraction_job_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Core display properties
    hex: Mapped[str] = mapped_column(String(7), nullable=False)
    rgb: Mapped[str] = mapped_column(String(20), nullable=False)
    hsl: Mapped[str | None] = mapped_column(String(30), nullable=True)
    hsv: Mapped[str | None] = mapped_column(String(30), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Design token properties
    design_intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    semantic_names: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON dict: simple/descriptive/emotional/technical/vibrancy
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Color analysis properties
    confidence: Mapped[float] = mapped_column(nullable=False)
    harmony: Mapped[str | None] = mapped_column(String(50), nullable=True)
    temperature: Mapped[str | None] = mapped_column(String(20), nullable=True)
    extraction_metadata: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON: maps field names to tool sources
    saturation_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lightness_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    usage: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Count & prominence
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    prominence_percentage: Mapped[float | None] = mapped_column(nullable=True)

    # Accessibility properties
    wcag_contrast_on_white: Mapped[float | None] = mapped_column(nullable=True)
    wcag_contrast_on_black: Mapped[float | None] = mapped_column(nullable=True)
    wcag_aa_compliant_text: Mapped[bool | None] = mapped_column(nullable=True)
    wcag_aaa_compliant_text: Mapped[bool | None] = mapped_column(nullable=True)
    wcag_aa_compliant_normal: Mapped[bool | None] = mapped_column(nullable=True)
    wcag_aaa_compliant_normal: Mapped[bool | None] = mapped_column(nullable=True)
    colorblind_safe: Mapped[bool | None] = mapped_column(nullable=True)

    # Color variants
    tint_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    shade_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    tone_color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Advanced properties
    closest_web_safe: Mapped[str | None] = mapped_column(String(7), nullable=True)
    closest_css_named: Mapped[str | None] = mapped_column(String(50), nullable=True)
    delta_e_to_dominant: Mapped[float | None] = mapped_column(nullable=True)
    is_neutral: Mapped[bool | None] = mapped_column(nullable=True)

    # ML/CV model properties
    kmeans_cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sam_segmentation_mask: Mapped[str | None] = mapped_column(Text, nullable=True)
    clip_embeddings: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    histogram_significance: Mapped[float | None] = mapped_column(nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    # Token library & curation
    library_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # FK to TokenLibrary
    role: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # 'primary', 'secondary', 'accent', 'neutral', etc. (user curation)
    provenance: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON: {"image_1": 0.95, "image_2": 0.88} - confidence from each source image

    def __repr__(self) -> str:
        return f"<ColorToken(id={self.id}, hex='{self.hex}', name='{self.name}', intent='{self.design_intent}')>"


class ExtractionSession(Base):
    """Batch extraction session - multiple images uploaded together"""

    __tablename__ = "extraction_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # e.g., "Brand Guidelines - Acme Corp"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Session metadata
    image_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_images: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array of image URLs/paths

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship()

    def __repr__(self) -> str:
        return f"<ExtractionSession(id={self.id}, name='{self.name}', images={self.image_count})>"


class TokenLibrary(Base):
    """Aggregated, deduplicated token set from an extraction session"""

    __tablename__ = "token_libraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)  # FK to ExtractionSession
    token_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'color', 'spacing', 'typography', etc.

    # Library metadata
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    statistics: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON: {"dominant_hue": ..., "mood": ..., "color_count": ...}

    # Curation status
    is_curated: Mapped[bool] = mapped_column(default=False, nullable=False)
    curation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<TokenLibrary(id={self.id}, session_id={self.session_id}, type='{self.token_type}')>"
        )


class TokenExport(Base):
    """Track exports for auditing and regeneration"""

    __tablename__ = "token_exports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    library_id: Mapped[int] = mapped_column(Integer, nullable=False)  # FK to TokenLibrary
    format: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'w3c', 'css', 'react', 'html', etc.

    # Export metadata
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    exported_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    def __repr__(self) -> str:
        return f"<TokenExport(id={self.id}, library_id={self.library_id}, format='{self.format}')>"
