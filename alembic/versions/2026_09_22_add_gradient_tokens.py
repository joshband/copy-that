"""add gradient tokens table

Revision ID: 2026_09_22_add_gradient_tokens
Revises: 2026_09_18_typo_quality
Create Date: 2026-09-22
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2026_09_22_add_gradient_tokens"
down_revision = "2026_09_18_typo_quality"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "gradient_tokens" not in inspector.get_table_names():
        op.create_table(
            "gradient_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), nullable=False, index=True),
            sa.Column("extraction_job_id", sa.Integer(), nullable=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("gradient_type", sa.String(length=50), nullable=False, server_default="linear"),
            sa.Column("angle", sa.Float(), nullable=False, server_default="90"),
            sa.Column("stops_json", sa.Text(), nullable=False),
            sa.Column("source", sa.String(length=50), nullable=False, server_default="cv"),
            sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
            sa.Column("axis", sa.String(length=50), nullable=True),
            sa.Column("confirmed_by", sa.String(length=50), nullable=True),
            sa.Column("extraction_metadata", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    indexes = (
        {ix["name"] for ix in inspector.get_indexes("gradient_tokens")}
        if "gradient_tokens" in inspector.get_table_names()
        else set()
    )
    if (
        "ix_gradient_tokens_project_id" not in indexes
        and "gradient_tokens" in inspector.get_table_names()
    ):
        op.create_index("ix_gradient_tokens_project_id", "gradient_tokens", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_gradient_tokens_project_id", table_name="gradient_tokens")
    op.drop_table("gradient_tokens")
