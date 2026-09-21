"""Add additional foreign key indexes for query performance

Revision ID: 2025_12_01_001
Revises: 2025_11_24_add_spacing_tokens
Create Date: 2025-12-01

Adds indexes on frequently queried foreign key columns that were missing:
- color_tokens.extraction_job_id
- spacing_tokens.extraction_job_id (project_id index exists from 2025_11_24)
- project_snapshots.project_id

Indexes already created earlier (skipped here):
- token_exports.library_id (2025_11_20_006)
- api_keys.user_id (2025_11_22_002)
- token_libraries.session_id (2025_11_20_006)
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2025_12_01_001"
down_revision: str | None = "2025_11_24_add_spacing_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _existing_indexes(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {ix["name"] for ix in inspector.get_indexes(table_name) if ix.get("name")}


def _create_index_if_missing(name: str, table_name: str, columns: list[str]) -> None:
    if name in _existing_indexes(table_name):
        return
    op.create_index(name, table_name, columns)


def upgrade() -> None:
    _create_index_if_missing(
        "ix_color_tokens_extraction_job_id",
        "color_tokens",
        ["extraction_job_id"],
    )
    _create_index_if_missing(
        "ix_spacing_tokens_extraction_job_id",
        "spacing_tokens",
        ["extraction_job_id"],
    )
    _create_index_if_missing(
        "ix_project_snapshots_project_id",
        "project_snapshots",
        ["project_id"],
    )
    # Intentionally not recreating:
    # - ix_token_exports_library_id (2025_11_20_006)
    # - ix_api_keys_user_id (2025_11_22_002)


def downgrade() -> None:
    # Only drop indexes this revision owns.
    for name, table in (
        ("ix_project_snapshots_project_id", "project_snapshots"),
        ("ix_spacing_tokens_extraction_job_id", "spacing_tokens"),
        ("ix_color_tokens_extraction_job_id", "color_tokens"),
    ):
        if name in _existing_indexes(table):
            op.drop_index(name, table_name=table)
