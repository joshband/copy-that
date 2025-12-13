"""Add additional foreign key indexes for query performance

Revision ID: 2025_12_01_001
Revises: 2025_11_24_add_spacing_tokens
Create Date: 2025-12-01

Adds indexes on frequently queried foreign key columns that were missing:
- color_tokens.extraction_job_id
- spacing_tokens.extraction_job_id (project_id index exists from 2025_11_24)
- project_snapshots.project_id
- token_libraries.session_id
- token_exports.library_id
- api_keys.user_id
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2025_12_01_001"
down_revision: str | None = "2025_11_24_add_spacing_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Color tokens - missing extraction_job_id index
    op.create_index(
        "ix_color_tokens_extraction_job_id",
        "color_tokens",
        ["extraction_job_id"],
    )

    # Spacing tokens - missing extraction_job_id index
    # Note: ix_spacing_tokens_project_id already created in 2025_11_24_add_spacing_tokens
    op.create_index(
        "ix_spacing_tokens_extraction_job_id",
        "spacing_tokens",
        ["extraction_job_id"],
    )

    # Project snapshots - missing project_id index
    op.create_index(
        "ix_project_snapshots_project_id",
        "project_snapshots",
        ["project_id"],
    )

    # Token libraries - missing session_id index
    op.create_index(
        "ix_token_libraries_session_id",
        "token_libraries",
        ["session_id"],
    )

    # Token exports - missing library_id index
    op.create_index(
        "ix_token_exports_library_id",
        "token_exports",
        ["library_id"],
    )

    # API keys - missing user_id index
    op.create_index(
        "ix_api_keys_user_id",
        "api_keys",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_api_keys_user_id", table_name="api_keys")
    op.drop_index("ix_token_exports_library_id", table_name="token_exports")
    op.drop_index("ix_token_libraries_session_id", table_name="token_libraries")
    op.drop_index("ix_project_snapshots_project_id", table_name="project_snapshots")
    op.drop_index("ix_spacing_tokens_extraction_job_id", table_name="spacing_tokens")
    # Note: ix_spacing_tokens_project_id managed by 2025_11_24_add_spacing_tokens
    op.drop_index("ix_color_tokens_extraction_job_id", table_name="color_tokens")
