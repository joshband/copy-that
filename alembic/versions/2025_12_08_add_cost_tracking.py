"""
Add cost tracking tables

Revision ID: 2025_12_08_cost_tracking
Revises: 2025_12_03_add_typography_and_font_tokens
Create Date: 2025-12-08 18:35:00
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "2025_12_08_cost_tracking"
down_revision = "2025_12_03_add_typography_and_font_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cost_records table
    op.create_table(
        "cost_records",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("service_name", sa.String(length=100), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("usage_metric", sa.String(length=200), nullable=True),
        sa.Column("period_start", sa.DateTime(), nullable=False),
        sa.Column("period_end", sa.DateTime(), nullable=False),
        sa.Column("raw_data", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for fast queries
    op.create_index("idx_provider_date", "cost_records", ["provider", "recorded_at"])
    op.create_index("idx_service_date", "cost_records", ["service_name", "recorded_at"])
    op.create_index("idx_period", "cost_records", ["period_start", "period_end"])
    op.create_index("idx_recorded_at", "cost_records", ["recorded_at"])

    # Create budget_configs table
    op.create_table(
        "budget_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("monthly_budget_usd", sa.Float(), nullable=False),
        sa.Column("alert_threshold", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("notification_email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.String(length=10), nullable=False, server_default="true"),
        sa.Column("last_alert_sent", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_index("idx_recorded_at", "cost_records")
    op.drop_index("idx_period", "cost_records")
    op.drop_index("idx_service_date", "cost_records")
    op.drop_index("idx_provider_date", "cost_records")
    op.drop_table("cost_records")
    op.drop_table("budget_configs")
