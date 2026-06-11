"""Create outreach_content table.

Revision ID: 001_create_outreach_tables
Revises: None (first Service-specific migration — chains from root)
Create Date: 2026-06-11
"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_create_outreach_tables"
down_revision: Optional[str] = "001_create_ai_execution_tables"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    """Create outreach_content table."""
    op.create_table(
        "outreach_content",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("content_type", sa.String(20), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("tone", sa.String(50), server_default=sa.text("'professional'"), nullable=True),
        sa.Column("target_role", sa.String(255), nullable=True),
        sa.Column("ai_agent_used", sa.String(100), nullable=True),
        sa.Column("ai_execution_id", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("parent_version_id", sa.Integer(), nullable=True),
        sa.Column("edit_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("recipient_name", sa.String(255), nullable=True),
        sa.Column("recipient_role", sa.String(255), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("personalization_hooks", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'"), nullable=True),
        sa.Column("is_template", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("template_name", sa.String(255), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="career",
    )

    op.create_index("ix_outreach_content_profile_id", "outreach_content", ["profile_id"], schema="career")
    op.create_index("ix_outreach_content_job_id", "outreach_content", ["job_id"], schema="career")
    op.create_index("ix_outreach_content_application_id", "outreach_content", ["application_id"], schema="career")
    op.create_index("ix_outreach_content_type_status", "outreach_content", ["content_type", "status"], schema="career")


def downgrade() -> None:
    """Drop outreach_content table."""
    op.drop_table("outreach_content", schema="career")
