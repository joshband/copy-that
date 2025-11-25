"""add spacing tokens table

Revision ID: 2025_11_24_add_spacing_tokens
Revises: 2025_11_22_002_add_user_authentication
Create Date: 2025-11-24
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2025_11_24_add_spacing_tokens"
down_revision = "2025_11_22_002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create table if it does not already exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "spacing_tokens" not in inspector.get_table_names():
        op.create_table(
            "spacing_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), nullable=False, index=True),
            sa.Column("extraction_job_id", sa.Integer(), nullable=True),
            sa.Column("value_px", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("semantic_role", sa.String(length=100), nullable=True),
            sa.Column("spacing_type", sa.String(length=50), nullable=True),
            sa.Column("category", sa.String(length=50), nullable=True),
            sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
            sa.Column("usage", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    # Create index if missing
    indexes = (
        {ix["name"] for ix in inspector.get_indexes("spacing_tokens")}
        if "spacing_tokens" in inspector.get_table_names()
        else set()
    )
    if (
        "ix_spacing_tokens_project_id" not in indexes
        and "spacing_tokens" in inspector.get_table_names()
    ):
        op.create_index("ix_spacing_tokens_project_id", "spacing_tokens", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_spacing_tokens_project_id", table_name="spacing_tokens")
    op.drop_table("spacing_tokens")
