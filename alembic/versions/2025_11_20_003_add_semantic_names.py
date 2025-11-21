"""Add semantic_names field to color_tokens table

Revision ID: 2025_11_20_003
Revises: 2025_11_19_002
Create Date: 2025-11-20 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2025_11_20_003"
down_revision: str | Sequence[str] | None = "2025_11_19_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - add semantic_names column to color_tokens."""
    op.add_column("color_tokens", sa.Column("semantic_names", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - remove semantic_names column from color_tokens."""
    op.drop_column("color_tokens", "semantic_names")
