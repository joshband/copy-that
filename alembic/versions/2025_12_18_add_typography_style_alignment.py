"""Add font style and text alignment to typography tokens.

Revision ID: 2025_12_18_typo_style_align
Revises: 2025_12_17_add_jobs_table
Create Date: 2025-12-18 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2025_12_18_typo_style_align"
down_revision: str | Sequence[str] | None = "2025_12_17_add_jobs_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add font_style and text_align columns to typography_tokens."""
    op.add_column(
        "typography_tokens",
        sa.Column("font_style", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "typography_tokens",
        sa.Column("text_align", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    """Remove font_style and text_align columns from typography_tokens."""
    op.drop_column("typography_tokens", "text_align")
    op.drop_column("typography_tokens", "font_style")
