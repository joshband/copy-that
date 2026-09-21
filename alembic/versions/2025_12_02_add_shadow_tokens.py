"""add shadow tokens table

Revision ID: 2025_12_02_add_shadow_tokens
Revises: 2025_12_01_001, 2025_11_24_add_project_snapshots
Create Date: 2025-12-02
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2025_12_02_add_shadow_tokens"
down_revision = ("2025_12_01_001", "2025_11_24_add_project_snapshots")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create table if it does not already exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "shadow_tokens" not in inspector.get_table_names():
        op.create_table(
            "shadow_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), nullable=False, index=True),
            sa.Column("extraction_job_id", sa.Integer(), nullable=True),
            # Shadow properties
            sa.Column("x_offset", sa.Float(), nullable=False),
            sa.Column("y_offset", sa.Float(), nullable=False),
            sa.Column("blur_radius", sa.Float(), nullable=False),
            sa.Column("spread_radius", sa.Float(), nullable=False, server_default="0"),
            sa.Column("color_hex", sa.String(length=7), nullable=False),
            sa.Column("opacity", sa.Float(), nullable=False, server_default="1.0"),
            # Classification
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("shadow_type", sa.String(length=50), nullable=True),
            sa.Column("semantic_role", sa.String(length=100), nullable=True),
            # Quality metrics
            sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
            sa.Column("extraction_metadata", sa.Text(), nullable=True),
            # Usage tracking
            sa.Column("usage", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=50), nullable=True),
            # Timestamps
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    # Create index if missing
    indexes = (
        {ix["name"] for ix in inspector.get_indexes("shadow_tokens")}
        if "shadow_tokens" in inspector.get_table_names()
        else set()
    )
    if (
        "ix_shadow_tokens_project_id" not in indexes
        and "shadow_tokens" in inspector.get_table_names()
    ):
        op.create_index("ix_shadow_tokens_project_id", "shadow_tokens", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_shadow_tokens_project_id", table_name="shadow_tokens")
    op.drop_table("shadow_tokens")
