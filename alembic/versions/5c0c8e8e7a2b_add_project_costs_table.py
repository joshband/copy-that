"""add project_costs table"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c0c8e8e7a2b"
down_revision: str | None = "2025_12_17_add_jobs_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_costs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("window", sa.String(length=10), nullable=False),
        sa.Column("total_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("soft_limit_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hard_limit_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_project_costs_project_id_window"),
        "project_costs",
        ["project_id", "window"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_project_costs_project_id_window"), table_name="project_costs")
    op.drop_table("project_costs")
