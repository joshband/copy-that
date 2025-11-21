"""Rename semantic_name column to design_intent for clarity

Revision ID: 2025_11_20_004
Revises: 2025_11_20_003
Create Date: 2025-11-20 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2025_11_20_004'
down_revision: str | Sequence[str] | None = '2025_11_20_003'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - rename semantic_name to design_intent."""
    op.alter_column('color_tokens', 'semantic_name', new_column_name='design_intent')


def downgrade() -> None:
    """Downgrade schema - rename design_intent back to semantic_name."""
    op.alter_column('color_tokens', 'design_intent', new_column_name='semantic_name')
