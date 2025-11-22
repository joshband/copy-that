"""Add performance indexes

Revision ID: 2025_11_22_001
Revises: 2025_11_20_006_add_session_and_library_models
Create Date: 2025-11-22

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2025_11_22_001"
down_revision: str | None = "2025_11_20_006_add_session_and_library_models"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Critical indexes for common queries
    op.create_index(
        "ix_color_tokens_project_id",
        "color_tokens",
        ["project_id"]
    )
    op.create_index(
        "ix_color_tokens_project_created",
        "color_tokens",
        ["project_id", sa.text("created_at DESC")]
    )
    op.create_index(
        "ix_extraction_jobs_project_id",
        "extraction_jobs",
        ["project_id"]
    )

    # Filtering indexes
    op.create_index(
        "ix_extraction_jobs_status",
        "extraction_jobs",
        ["status"]
    )
    op.create_index(
        "ix_color_tokens_design_intent",
        "color_tokens",
        ["design_intent"]
    )
    op.create_index(
        "ix_extraction_jobs_type",
        "extraction_jobs",
        ["extraction_type"]
    )


def downgrade() -> None:
    op.drop_index("ix_extraction_jobs_type", table_name="extraction_jobs")
    op.drop_index("ix_color_tokens_design_intent", table_name="color_tokens")
    op.drop_index("ix_extraction_jobs_status", table_name="extraction_jobs")
    op.drop_index("ix_extraction_jobs_project_id", table_name="extraction_jobs")
    op.drop_index("ix_color_tokens_project_created", table_name="color_tokens")
    op.drop_index("ix_color_tokens_project_id", table_name="color_tokens")
