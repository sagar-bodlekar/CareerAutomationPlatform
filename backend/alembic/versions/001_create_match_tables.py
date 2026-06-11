"""Create job_matches table.

Revision ID: 001_create_match_tables
Revises: 001_create_job_tables
Create Date: 2026-06-11
"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_match_tables"
down_revision: Optional[str] = "001_create_job_tables"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    """Create job_matches table."""
    op.create_table(
        "job_matches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("skills_score", sa.Float(), nullable=True),
        sa.Column("experience_score", sa.Float(), nullable=True),
        sa.Column("education_score", sa.Float(), nullable=True),
        sa.Column("location_score", sa.Float(), nullable=True),
        sa.Column("title_score", sa.Float(), nullable=True),
        sa.Column("matched_skills", postgresql.JSONB(), nullable=True),
        sa.Column("missing_skills", postgresql.JSONB(), nullable=True),
        sa.Column("extra_skills", postgresql.JSONB(), nullable=True),
        sa.Column("skill_gaps", postgresql.JSONB(), nullable=True),
        sa.Column("match_summary", sa.Text(), nullable=True),
        sa.Column("ai_enhanced", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("ai_recommendation", sa.Text(), nullable=True),
        sa.Column("ai_match_data", postgresql.JSONB(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("is_top_match", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'"), nullable=False),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="career",
    )

    op.create_index("ix_job_matches_profile_id", "job_matches", ["profile_id"], schema="career")
    op.create_index("ix_job_matches_job_id", "job_matches", ["job_id"], schema="career")
    op.create_index("ix_job_matches_profile_score", "job_matches", ["profile_id", "overall_score"], schema="career")
    op.create_index(
        "ix_job_matches_job_profile",
        "job_matches",
        ["job_id", "profile_id"],
        schema="career",
        unique=True,
    )


def downgrade() -> None:
    """Drop job_matches table."""
    op.drop_table("job_matches", schema="career")
