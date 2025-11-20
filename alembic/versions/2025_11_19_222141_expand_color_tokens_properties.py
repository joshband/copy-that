"""Expand color_tokens with all 50+ advanced properties

Revision ID: 2025_11_19_002
Revises: 2025_11_19_001
Create Date: 2025-11-19 22:21:41.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_19_002'
down_revision: Union[str, Sequence[str], None] = '2025_11_19_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with all color token properties."""
    # Color format properties
    op.add_column('color_tokens', sa.Column('hsl', sa.String(length=30), nullable=True))
    op.add_column('color_tokens', sa.Column('hsv', sa.String(length=30), nullable=True))

    # Design token properties
    op.add_column('color_tokens', sa.Column('category', sa.String(length=50), nullable=True))

    # Color analysis properties
    op.add_column('color_tokens', sa.Column('temperature', sa.String(length=20), nullable=True))
    op.add_column('color_tokens', sa.Column('saturation_level', sa.String(length=20), nullable=True))
    op.add_column('color_tokens', sa.Column('lightness_level', sa.String(length=20), nullable=True))

    # Count & prominence
    op.add_column('color_tokens', sa.Column('count', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('color_tokens', sa.Column('prominence_percentage', sa.Float(), nullable=True))

    # Accessibility (WCAG) properties
    op.add_column('color_tokens', sa.Column('wcag_contrast_on_white', sa.Float(), nullable=True))
    op.add_column('color_tokens', sa.Column('wcag_contrast_on_black', sa.Float(), nullable=True))
    op.add_column('color_tokens', sa.Column('wcag_aa_compliant_text', sa.Boolean(), nullable=True))
    op.add_column('color_tokens', sa.Column('wcag_aaa_compliant_text', sa.Boolean(), nullable=True))
    op.add_column('color_tokens', sa.Column('wcag_aa_compliant_normal', sa.Boolean(), nullable=True))
    op.add_column('color_tokens', sa.Column('wcag_aaa_compliant_normal', sa.Boolean(), nullable=True))
    op.add_column('color_tokens', sa.Column('colorblind_safe', sa.Boolean(), nullable=True))

    # Color variants
    op.add_column('color_tokens', sa.Column('tint_color', sa.String(length=7), nullable=True))
    op.add_column('color_tokens', sa.Column('shade_color', sa.String(length=7), nullable=True))
    op.add_column('color_tokens', sa.Column('tone_color', sa.String(length=7), nullable=True))

    # Advanced properties
    op.add_column('color_tokens', sa.Column('closest_web_safe', sa.String(length=7), nullable=True))
    op.add_column('color_tokens', sa.Column('closest_css_named', sa.String(length=50), nullable=True))
    op.add_column('color_tokens', sa.Column('delta_e_to_dominant', sa.Float(), nullable=True))
    op.add_column('color_tokens', sa.Column('is_neutral', sa.Boolean(), nullable=True))

    # ML/CV model properties
    op.add_column('color_tokens', sa.Column('kmeans_cluster_id', sa.Integer(), nullable=True))
    op.add_column('color_tokens', sa.Column('sam_segmentation_mask', sa.Text(), nullable=True))
    op.add_column('color_tokens', sa.Column('clip_embeddings', sa.Text(), nullable=True))
    op.add_column('color_tokens', sa.Column('histogram_significance', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove all added columns in reverse order
    op.drop_column('color_tokens', 'histogram_significance')
    op.drop_column('color_tokens', 'clip_embeddings')
    op.drop_column('color_tokens', 'sam_segmentation_mask')
    op.drop_column('color_tokens', 'kmeans_cluster_id')

    op.drop_column('color_tokens', 'is_neutral')
    op.drop_column('color_tokens', 'delta_e_to_dominant')
    op.drop_column('color_tokens', 'closest_css_named')
    op.drop_column('color_tokens', 'closest_web_safe')

    op.drop_column('color_tokens', 'tone_color')
    op.drop_column('color_tokens', 'shade_color')
    op.drop_column('color_tokens', 'tint_color')

    op.drop_column('color_tokens', 'colorblind_safe')
    op.drop_column('color_tokens', 'wcag_aaa_compliant_normal')
    op.drop_column('color_tokens', 'wcag_aa_compliant_normal')
    op.drop_column('color_tokens', 'wcag_aaa_compliant_text')
    op.drop_column('color_tokens', 'wcag_aa_compliant_text')
    op.drop_column('color_tokens', 'wcag_contrast_on_black')
    op.drop_column('color_tokens', 'wcag_contrast_on_white')

    op.drop_column('color_tokens', 'prominence_percentage')
    op.drop_column('color_tokens', 'count')

    op.drop_column('color_tokens', 'lightness_level')
    op.drop_column('color_tokens', 'saturation_level')
    op.drop_column('color_tokens', 'temperature')

    op.drop_column('color_tokens', 'category')

    op.drop_column('color_tokens', 'hsv')
    op.drop_column('color_tokens', 'hsl')
