"""add typography quality columns

Revision ID: 2026_09_18_typo_quality
Revises: 2026_09_18_add_layout_tokens
Create Date: 2026-09-18
"""

import sqlalchemy as sa

from alembic import op

revision = "2026_09_18_typo_quality"
down_revision = "2026_09_18_add_layout_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "typography_tokens" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("typography_tokens")}
    if "prominence" not in existing:
        op.add_column(
            "typography_tokens",
            sa.Column("prominence", sa.Float(), nullable=True),
        )
    if "is_readable" not in existing:
        op.add_column(
            "typography_tokens",
            sa.Column("is_readable", sa.Boolean(), nullable=True),
        )
    if "readability_score" not in existing:
        op.add_column(
            "typography_tokens",
            sa.Column("readability_score", sa.Float(), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "typography_tokens" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("typography_tokens")}
    if "readability_score" in existing:
        op.drop_column("typography_tokens", "readability_score")
    if "is_readable" in existing:
        op.drop_column("typography_tokens", "is_readable")
    if "prominence" in existing:
        op.drop_column("typography_tokens", "prominence")
