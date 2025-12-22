"""Merge heads.

Revision ID: 2025_12_19_merge_heads
Revises: 5c0c8e8e7a2b, 2025_12_18_add_typography_style_alignment
Create Date: 2025-12-19 00:00:00
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "2025_12_19_merge_heads"
down_revision: str | Sequence[str] | None = (
    "5c0c8e8e7a2b",
    "2025_12_18_add_typography_style_alignment",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge heads."""


def downgrade() -> None:
    """Unmerge heads."""
