"""Add extraction_metadata field to track extraction tool sources

Revision ID: 2025_11_20_005
Revises: 2025_11_20_004
Create Date: 2025-11-20 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2025_11_20_005"
down_revision: str | Sequence[str] | None = "2025_11_20_004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - add extraction_metadata column to color_tokens."""
    op.add_column("color_tokens", sa.Column("extraction_metadata", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - remove extraction_metadata column from color_tokens."""
    op.drop_column("color_tokens", "extraction_metadata")
