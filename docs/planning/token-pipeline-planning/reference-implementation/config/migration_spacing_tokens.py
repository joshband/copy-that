"""
Add spacing_tokens table

REFERENCE IMPLEMENTATION - This is planning/documentation code showing how the
Alembic migration for the spacing_tokens table should be structured when
implemented. This code is not meant to be run directly but serves as a complete
reference for implementing the actual migration.

Revision ID: spacing_tokens_001
Revises: <previous_migration_id>
Create Date: 2025-11-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic
revision = "spacing_tokens_001"
down_revision = None  # Set to previous migration ID when integrating
branch_labels = None
depends_on = None


def upgrade():
    """
    Create the spacing_tokens table with all columns, indexes, and constraints.
    """
    # ==========================================================================
    # Create spacing_tokens table
    # ==========================================================================
    op.create_table(
        "spacing_tokens",

        # Primary key
        sa.Column("id", sa.Integer(), nullable=False),

        # Foreign keys
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("library_id", sa.Integer(), nullable=True),
        sa.Column("extraction_job_id", sa.Integer(), nullable=True),

        # Core spacing values
        sa.Column("value_px", sa.Integer(), nullable=False,
                  comment="Spacing value in pixels"),
        sa.Column("value_rem", sa.Float(), nullable=False,
                  comment="Spacing value in rem units (base 16px)"),
        sa.Column("value_em", sa.Float(), nullable=False,
                  comment="Spacing value in em units"),

        # Scale information
        sa.Column("scale", sa.String(20), nullable=False,
                  comment="Position in spacing scale (xs, sm, md, lg, xl, etc.)"),
        sa.Column("base_unit", sa.Integer(), default=4,
                  comment="Detected base unit (4px or 8px system)"),
        sa.Column("multiplier", sa.Float(), nullable=False,
                  comment="Multiplier of base unit"),

        # Semantic information
        sa.Column("name", sa.String(255), nullable=False,
                  comment="Generated semantic name"),
        sa.Column("spacing_type", sa.String(50), nullable=False,
                  comment="Type of spacing (padding, margin, gap, inset, gutter)"),
        sa.Column("design_intent", sa.String(500), nullable=True,
                  comment="AI-detected design intent"),

        # Context information
        sa.Column("use_case", sa.String(500), nullable=True,
                  comment="Suggested use case"),
        sa.Column("context", sa.String(500), nullable=True,
                  comment="Where spacing was detected in the design"),

        # Analysis results
        sa.Column("confidence", sa.Float(), nullable=False,
                  comment="Extraction confidence score (0.0-1.0)"),
        sa.Column("is_grid_compliant", sa.Boolean(), default=True,
                  comment="Fits common grid systems (4px, 8px)"),
        sa.Column("rhythm_consistency", sa.String(50), nullable=True,
                  comment="Rhythm analysis (consistent, irregular, mixed)"),

        # JSON fields for complex data
        sa.Column("responsive_scales", postgresql.JSONB(), nullable=True,
                  comment="Responsive breakpoint adjustments"),
        sa.Column("semantic_names", postgresql.JSONB(), nullable=True,
                  comment="Multiple naming schemes (simple, descriptive, contextual)"),
        sa.Column("related_to", postgresql.JSONB(), nullable=True,
                  comment="Related spacing token IDs"),
        sa.Column("component_usage", postgresql.JSONB(), nullable=True,
                  comment="List of components using this spacing"),
        sa.Column("extraction_metadata", postgresql.JSONB(), nullable=True,
                  comment="Extraction provenance and algorithm details"),
        sa.Column("provenance", postgresql.JSONB(), nullable=True,
                  comment="Image sources with confidence scores"),

        # Timestamps
        sa.Column("created_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now(),
                  comment="Record creation timestamp"),
        sa.Column("updated_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now(),
                  onupdate=sa.func.now(),
                  comment="Record last update timestamp"),

        # Primary key constraint
        sa.PrimaryKeyConstraint("id"),
    )

    # ==========================================================================
    # Create foreign key constraints
    # ==========================================================================

    op.create_foreign_key(
        "fk_spacing_tokens_project",
        "spacing_tokens",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE"
    )

    op.create_foreign_key(
        "fk_spacing_tokens_library",
        "spacing_tokens",
        "token_libraries",
        ["library_id"],
        ["id"],
        ondelete="SET NULL"
    )

    op.create_foreign_key(
        "fk_spacing_tokens_extraction_job",
        "spacing_tokens",
        "extraction_jobs",
        ["extraction_job_id"],
        ["id"],
        ondelete="SET NULL"
    )

    # ==========================================================================
    # Create indexes for common queries
    # ==========================================================================

    # Primary query patterns
    op.create_index(
        "ix_spacing_tokens_project_id",
        "spacing_tokens",
        ["project_id"],
        comment="Fast lookup by project"
    )

    op.create_index(
        "ix_spacing_tokens_library_id",
        "spacing_tokens",
        ["library_id"],
        comment="Fast lookup by token library"
    )

    op.create_index(
        "ix_spacing_tokens_extraction_job_id",
        "spacing_tokens",
        ["extraction_job_id"],
        comment="Fast lookup by extraction job"
    )

    # Value-based queries
    op.create_index(
        "ix_spacing_tokens_value_px",
        "spacing_tokens",
        ["value_px"],
        comment="Fast lookup by pixel value"
    )

    op.create_index(
        "ix_spacing_tokens_scale",
        "spacing_tokens",
        ["scale"],
        comment="Fast lookup by scale position"
    )

    op.create_index(
        "ix_spacing_tokens_spacing_type",
        "spacing_tokens",
        ["spacing_type"],
        comment="Fast filtering by spacing type"
    )

    # Compound indexes for common query patterns
    op.create_index(
        "ix_spacing_tokens_project_scale",
        "spacing_tokens",
        ["project_id", "scale"],
        comment="Fast project + scale queries"
    )

    op.create_index(
        "ix_spacing_tokens_project_value",
        "spacing_tokens",
        ["project_id", "value_px"],
        comment="Fast project + value queries"
    )

    op.create_index(
        "ix_spacing_tokens_project_type",
        "spacing_tokens",
        ["project_id", "spacing_type"],
        comment="Fast project + type queries"
    )

    # Confidence filtering
    op.create_index(
        "ix_spacing_tokens_confidence",
        "spacing_tokens",
        ["confidence"],
        comment="Fast filtering by confidence"
    )

    # Timestamp queries
    op.create_index(
        "ix_spacing_tokens_created_at",
        "spacing_tokens",
        ["created_at"],
        comment="Fast sorting by creation date"
    )

    # ==========================================================================
    # Create GIN indexes for JSONB columns
    # ==========================================================================

    op.create_index(
        "ix_spacing_tokens_semantic_names_gin",
        "spacing_tokens",
        ["semantic_names"],
        postgresql_using="gin",
        comment="Fast JSONB queries on semantic names"
    )

    op.create_index(
        "ix_spacing_tokens_component_usage_gin",
        "spacing_tokens",
        ["component_usage"],
        postgresql_using="gin",
        comment="Fast JSONB queries on component usage"
    )

    op.create_index(
        "ix_spacing_tokens_provenance_gin",
        "spacing_tokens",
        ["provenance"],
        postgresql_using="gin",
        comment="Fast JSONB queries on provenance"
    )


def downgrade():
    """
    Drop the spacing_tokens table and all associated objects.
    """
    # Drop indexes (automatically dropped with table, but explicit for clarity)
    op.drop_index("ix_spacing_tokens_provenance_gin", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_component_usage_gin", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_semantic_names_gin", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_created_at", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_confidence", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_project_type", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_project_value", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_project_scale", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_spacing_type", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_scale", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_value_px", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_extraction_job_id", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_library_id", table_name="spacing_tokens")
    op.drop_index("ix_spacing_tokens_project_id", table_name="spacing_tokens")

    # Drop foreign key constraints
    op.drop_constraint("fk_spacing_tokens_extraction_job", "spacing_tokens", type_="foreignkey")
    op.drop_constraint("fk_spacing_tokens_library", "spacing_tokens", type_="foreignkey")
    op.drop_constraint("fk_spacing_tokens_project", "spacing_tokens", type_="foreignkey")

    # Drop the table
    op.drop_table("spacing_tokens")


# =============================================================================
# SQLite Compatibility (for testing)
# =============================================================================
# Note: The above migration uses PostgreSQL-specific features (JSONB, GIN indexes).
# For SQLite testing, use this alternative:

def upgrade_sqlite():
    """
    SQLite-compatible version of upgrade (for testing only).
    """
    op.create_table(
        "spacing_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("library_id", sa.Integer(), nullable=True),
        sa.Column("extraction_job_id", sa.Integer(), nullable=True),
        sa.Column("value_px", sa.Integer(), nullable=False),
        sa.Column("value_rem", sa.Float(), nullable=False),
        sa.Column("value_em", sa.Float(), nullable=False),
        sa.Column("scale", sa.String(20), nullable=False),
        sa.Column("base_unit", sa.Integer(), default=4),
        sa.Column("multiplier", sa.Float(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("spacing_type", sa.String(50), nullable=False),
        sa.Column("design_intent", sa.String(500), nullable=True),
        sa.Column("use_case", sa.String(500), nullable=True),
        sa.Column("context", sa.String(500), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("is_grid_compliant", sa.Boolean(), default=True),
        sa.Column("rhythm_consistency", sa.String(50), nullable=True),
        # SQLite uses TEXT for JSON storage
        sa.Column("responsive_scales", sa.Text(), nullable=True),
        sa.Column("semantic_names", sa.Text(), nullable=True),
        sa.Column("related_to", sa.Text(), nullable=True),
        sa.Column("component_usage", sa.Text(), nullable=True),
        sa.Column("extraction_metadata", sa.Text(), nullable=True),
        sa.Column("provenance", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        # SQLite supports foreign keys but they're not enforced by default
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["library_id"], ["token_libraries.id"]),
        sa.ForeignKeyConstraint(["extraction_job_id"], ["extraction_jobs.id"]),
    )

    # Basic indexes for SQLite
    op.create_index("ix_spacing_tokens_project_id", "spacing_tokens", ["project_id"])
    op.create_index("ix_spacing_tokens_value_px", "spacing_tokens", ["value_px"])
    op.create_index("ix_spacing_tokens_scale", "spacing_tokens", ["scale"])
