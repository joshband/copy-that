"""Add ExtractionSession, TokenLibrary, TokenExport models and update ColorToken

Revision ID: 2025_11_20_006
Revises: 2025_11_20_005
Create Date: 2025-11-20 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2025_11_20_006'
down_revision: str | Sequence[str] | None = '2025_11_20_005'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - add session/library models and update ColorToken."""

    # Create ExtractionSession table
    op.create_table(
        'extraction_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('source_images', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create TokenLibrary table
    op.create_table(
        'token_libraries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('token_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('statistics', sa.Text(), nullable=True),
        sa.Column('is_curated', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('curation_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['extraction_sessions.id'], )
    )

    # Create TokenExport table
    op.create_table(
        'token_exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('library_id', sa.Integer(), nullable=False),
        sa.Column('format', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('exported_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['library_id'], ['token_libraries.id'], )
    )

    # Update ColorToken table
    op.add_column('color_tokens', sa.Column('library_id', sa.Integer(), nullable=True))
    op.add_column('color_tokens', sa.Column('role', sa.String(length=50), nullable=True))
    op.add_column('color_tokens', sa.Column('provenance', sa.Text(), nullable=True))

    # Add indexes for performance
    op.create_index('ix_extraction_sessions_project_id', 'extraction_sessions', ['project_id'])
    op.create_index('ix_token_libraries_session_id', 'token_libraries', ['session_id'])
    op.create_index('ix_token_libraries_token_type', 'token_libraries', ['token_type'])
    op.create_index('ix_token_exports_library_id', 'token_exports', ['library_id'])
    op.create_index('ix_color_tokens_library_id', 'color_tokens', ['library_id'])
    op.create_index('ix_color_tokens_role', 'color_tokens', ['role'])


def downgrade() -> None:
    """Downgrade schema - remove session/library models and revert ColorToken."""

    # Drop indexes
    op.drop_index('ix_color_tokens_role', table_name='color_tokens')
    op.drop_index('ix_color_tokens_library_id', table_name='color_tokens')
    op.drop_index('ix_token_exports_library_id', table_name='token_exports')
    op.drop_index('ix_token_libraries_token_type', table_name='token_libraries')
    op.drop_index('ix_token_libraries_session_id', table_name='token_libraries')
    op.drop_index('ix_extraction_sessions_project_id', table_name='extraction_sessions')

    # Drop columns from ColorToken
    op.drop_column('color_tokens', 'provenance')
    op.drop_column('color_tokens', 'role')
    op.drop_column('color_tokens', 'library_id')

    # Drop tables
    op.drop_table('token_exports')
    op.drop_table('token_libraries')
    op.drop_table('extraction_sessions')
