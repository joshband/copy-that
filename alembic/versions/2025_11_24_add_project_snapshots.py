"""add project snapshots table

Revision ID: 2025_11_24_add_project_snapshots
Revises: 2025_11_24_add_spacing_tokens
Create Date: 2025-11-24
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2025_11_24_add_project_snapshots"
down_revision = "2025_11_24_add_spacing_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if "project_snapshots" in tables:
        return
    op.create_table(
        "project_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_index("ix_project_snapshots_project_id", table_name="project_snapshots")
    op.drop_table("project_snapshots")
