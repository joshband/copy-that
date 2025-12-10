"""
Add missing color token fields for advanced color analysis

Revision ID: 2025_12_09_add_color_token_fields
Revises: 2025_12_08_cost_tracking
Create Date: 2025-12-09 20:35:00
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = "2025_12_09_add_color_token_fields"
down_revision = "2025_12_08_cost_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to color_tokens table
    op.add_column("color_tokens", sa.Column("harmony_confidence", sa.Float(), nullable=True))
    op.add_column("color_tokens", sa.Column("hue_angles", sa.Text(), nullable=True))
    op.add_column("color_tokens", sa.Column("background_role", sa.String(length=50), nullable=True))
    op.add_column(
        "color_tokens", sa.Column("contrast_category", sa.String(length=20), nullable=True)
    )
    op.add_column("color_tokens", sa.Column("foreground_role", sa.String(length=50), nullable=True))
    op.add_column("color_tokens", sa.Column("is_accent", sa.Boolean(), nullable=True))
    op.add_column("color_tokens", sa.Column("state_variants", sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove columns from color_tokens table
    op.drop_column("color_tokens", "state_variants")
    op.drop_column("color_tokens", "is_accent")
    op.drop_column("color_tokens", "foreground_role")
    op.drop_column("color_tokens", "contrast_category")
    op.drop_column("color_tokens", "background_role")
    op.drop_column("color_tokens", "hue_angles")
    op.drop_column("color_tokens", "harmony_confidence")
