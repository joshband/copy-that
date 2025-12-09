"""
Cost Tracking Database Models
Stores historical cost data from all providers (GCP, Neon, Anthropic, OpenAI)
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Index, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CostRecord(Base):
    """
    Historical cost tracking record

    Stores daily snapshots of costs from all providers
    """

    __tablename__ = "cost_records"

    id = Column(String, primary_key=True)  # UUID
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Provider and service
    provider = Column(String(50), nullable=False, index=True)  # GCP, Neon, Anthropic, OpenAI
    service_name = Column(String(100), nullable=False)  # Cloud Run, Claude API, etc.

    # Cost data
    cost_usd = Column(Float, nullable=False)
    usage_metric = Column(String(200), nullable=True)  # e.g., "1.2M tokens", "45 requests"

    # Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Raw API response (for debugging)
    raw_data = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_provider_date", "provider", "recorded_at"),
        Index("idx_service_date", "service_name", "recorded_at"),
        Index("idx_period", "period_start", "period_end"),
    )


class BudgetConfig(Base):
    """
    Budget configuration and alerts
    """

    __tablename__ = "budget_configs"

    id = Column(String, primary_key=True)  # UUID

    # Budget settings
    monthly_budget_usd = Column(Float, nullable=False)
    alert_threshold = Column(Float, default=0.8)  # Alert at 80%
    notification_email = Column(String(255), nullable=True)

    # Status
    is_active = Column(String(10), default="true")
    last_alert_sent = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
