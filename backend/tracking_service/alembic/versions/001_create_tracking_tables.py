"""Create tracking service tables with UUID profile_id columns.

Revision ID: 001_create_tracking_tables
Revises: None
Create Date: 2026-06-19
"""
from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_create_tracking_tables"
down_revision: Optional[str] = None
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    """Create application_stats, application_funnels, and daily_application_counts tables."""
    schema = "career"

    op.create_table(
        "application_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_applications", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("total_sent", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("total_delivered", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("total_opened", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("total_replied", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("total_interviews", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("total_offers", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("total_rejected", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("avg_match_score", sa.Float(), nullable=True),
        sa.Column("avg_response_time_hours", sa.Float(), nullable=True),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index(
        "ix_application_stats_profile_id",
        "application_stats",
        ["profile_id"],
        schema=schema,
    )

    op.create_table(
        "application_funnels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status_counts", postgresql.JSONB(), nullable=False),
        sa.Column("snapshot_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index(
        "ix_application_funnels_profile_id",
        "application_funnels",
        ["profile_id"],
        schema=schema,
    )
    op.create_index(
        "ix_application_funnels_snapshot_date",
        "application_funnels",
        ["snapshot_date"],
        schema=schema,
    )

    op.create_table(
        "daily_application_counts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("sent_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("interview_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("offer_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index(
        "ix_daily_counts_profile_id",
        "daily_application_counts",
        ["profile_id"],
        schema=schema,
    )
    op.create_index(
        "ix_daily_counts_date",
        "daily_application_counts",
        ["date"],
        schema=schema,
    )


def downgrade() -> None:
    """Drop all tracking service tables."""
    schema = "career"
    op.drop_table("daily_application_counts", schema=schema)
    op.drop_table("application_funnels", schema=schema)
    op.drop_table("application_stats", schema=schema)
