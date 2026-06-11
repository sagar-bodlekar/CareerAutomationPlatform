"""Create ai_execution_logs table.

Revision ID: 001_create_ai_execution_tables
Revises: 001_create_match_tables
Create Date: 2026-06-11
"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_ai_execution_tables"
down_revision: Optional[str] = "001_create_match_tables"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    """Create ai_execution_logs table."""
    op.create_table(
        "ai_execution_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("model_provider", sa.String(50), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("prompt_template", sa.String(255), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("cost_estimate", sa.Float(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("success", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("provider_fallback_used", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("input_preview", sa.String(500), nullable=True),
        sa.Column("output_preview", sa.String(500), nullable=True),
        sa.Column("raw_request", postgresql.JSONB(), nullable=True),
        sa.Column("raw_response", postgresql.JSONB(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("profile_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="career",
    )

    op.create_index("ix_ai_execution_logs_agent", "ai_execution_logs", ["agent_name"], schema="career")
    op.create_index("ix_ai_execution_logs_created", "ai_execution_logs", ["created_at"], schema="career")


def downgrade() -> None:
    """Drop ai_execution_logs table."""
    op.drop_table("ai_execution_logs", schema="career")
