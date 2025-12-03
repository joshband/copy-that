"""add typography and font tokens tables

Revision ID: 2025_12_03_add_typography_and_font_tokens
Revises: 2025_12_02_add_shadow_tokens
Create Date: 2025-12-03
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2025_12_03_add_typography_and_font_tokens"
down_revision = "2025_12_02_add_shadow_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Create typography_tokens table if it does not already exist
    if "typography_tokens" not in inspector.get_table_names():
        op.create_table(
            "typography_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), nullable=False, index=True),
            sa.Column("extraction_job_id", sa.Integer(), nullable=True),
            # Typography properties
            sa.Column("font_family", sa.String(length=128), nullable=False),
            sa.Column("font_weight", sa.Integer(), nullable=False),
            sa.Column("font_size", sa.Integer(), nullable=False),
            sa.Column("line_height", sa.Float(), nullable=False),
            sa.Column("letter_spacing", sa.Float(), nullable=True),
            sa.Column("text_transform", sa.String(length=20), nullable=True),
            # Design properties
            sa.Column("name", sa.String(length=128), nullable=True),
            sa.Column("semantic_role", sa.String(length=50), nullable=True),
            sa.Column("category", sa.String(length=50), nullable=True),
            # Quality metrics
            sa.Column("confidence", sa.Float(), nullable=False, server_default="0.8"),
            sa.Column("extraction_metadata", sa.Text(), nullable=True),
            # Usage tracking
            sa.Column("usage", sa.Text(), nullable=True),
            # Timestamps
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    # Create index if missing
    indexes = (
        {ix["name"] for ix in inspector.get_indexes("typography_tokens")}
        if "typography_tokens" in inspector.get_table_names()
        else set()
    )
    if (
        "ix_typography_tokens_project_id" not in indexes
        and "typography_tokens" in inspector.get_table_names()
    ):
        op.create_index("ix_typography_tokens_project_id", "typography_tokens", ["project_id"])

    # Create font_family_tokens table if it does not already exist
    if "font_family_tokens" not in inspector.get_table_names():
        op.create_table(
            "font_family_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), nullable=False, index=True),
            # Font properties
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False),
            sa.Column("font_file_url", sa.String(length=512), nullable=True),
            sa.Column("fallback_stack", sa.Text(), nullable=False),
            # Quality metrics
            sa.Column("confidence", sa.Float(), nullable=False, server_default="0.9"),
            # Timestamps
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    # Create index if missing
    indexes = (
        {ix["name"] for ix in inspector.get_indexes("font_family_tokens")}
        if "font_family_tokens" in inspector.get_table_names()
        else set()
    )
    if (
        "ix_font_family_tokens_project_id" not in indexes
        and "font_family_tokens" in inspector.get_table_names()
    ):
        op.create_index("ix_font_family_tokens_project_id", "font_family_tokens", ["project_id"])

    # Create font_size_tokens table if it does not already exist
    if "font_size_tokens" not in inspector.get_table_names():
        op.create_table(
            "font_size_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), nullable=False, index=True),
            # Size properties
            sa.Column("size_px", sa.Integer(), nullable=False),
            sa.Column("size_rem", sa.Float(), nullable=False),
            sa.Column("semantic_name", sa.String(length=50), nullable=True),
            # Quality metrics
            sa.Column("confidence", sa.Float(), nullable=False, server_default="0.9"),
            # Timestamps
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    # Create index if missing
    indexes = (
        {ix["name"] for ix in inspector.get_indexes("font_size_tokens")}
        if "font_size_tokens" in inspector.get_table_names()
        else set()
    )
    if (
        "ix_font_size_tokens_project_id" not in indexes
        and "font_size_tokens" in inspector.get_table_names()
    ):
        op.create_index("ix_font_size_tokens_project_id", "font_size_tokens", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_font_size_tokens_project_id", table_name="font_size_tokens")
    op.drop_table("font_size_tokens")
    op.drop_index("ix_font_family_tokens_project_id", table_name="font_family_tokens")
    op.drop_table("font_family_tokens")
    op.drop_index("ix_typography_tokens_project_id", table_name="typography_tokens")
    op.drop_table("typography_tokens")
