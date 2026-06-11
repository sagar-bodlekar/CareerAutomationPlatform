"""Create applications and application_events tables.

Revision ID: 001_create_application_tables
Revises: 001_create_outreach_tables
Create Date: 2026-06-11
"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_create_application_tables"
down_revision: Optional[str] = "001_create_outreach_tables"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    """Create applications and application_events tables."""
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(30), server_default=sa.text("'draft'"), nullable=False),
        sa.Column("previous_status", sa.String(30), nullable=True),
        sa.Column("resume_id", sa.Integer(), nullable=True),
        sa.Column("resume_file_id", sa.Integer(), nullable=True),
        sa.Column("cover_letter_id", sa.Integer(), nullable=True),
        sa.Column("email_id", sa.Integer(), nullable=True),
        sa.Column("package_data", postgresql.JSONB(), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("job_title", sa.String(255), nullable=True),
        sa.Column("job_location", sa.String(255), nullable=True),
        sa.Column("job_url", sa.String(1000), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_status", sa.String(30), nullable=True),
        sa.Column("delivery_message_id", sa.String(255), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("match_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="career",
    )

    op.create_index("ix_applications_profile_id", "applications", ["profile_id"], schema="career")
    op.create_index("ix_applications_job_id", "applications", ["job_id"], schema="career")
    op.create_index("ix_applications_user_id", "applications", ["user_id"], schema="career")
    op.create_index("ix_applications_status", "applications", ["status"], schema="career")
    op.create_index("ix_applications_profile_status", "applications", ["profile_id", "status"], schema="career")

    op.create_table(
        "application_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("career.applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_status", sa.String(30), nullable=True),
        sa.Column("to_status", sa.String(30), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("actor", sa.String(50), server_default=sa.text("'system'"), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="career",
    )

    op.create_index("ix_application_events_app_id", "application_events", ["application_id"], schema="career")
    op.create_index("ix_application_events_created", "application_events", ["created_at"], schema="career")


def downgrade() -> None:
    """Drop application_events and applications tables."""
    op.drop_table("application_events", schema="career")
    op.drop_table("applications", schema="career")
