"""Add languages table and gender column to personal_info

Revision ID: 002_add_languages_and_gender
Revises: 001_create_profile_tables
Create Date: 2026-06-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_add_languages_and_gender"
down_revision: Union[str, None] = "001_create_profile_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add languages table and gender column to personal_info."""

    # Add gender column to personal_info
    op.add_column(
        "personal_info",
        sa.Column("gender", sa.String(50), nullable=True),
        schema="career",
    )

    # Create languages table
    op.create_table(
        "languages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("proficiency", sa.String(20), nullable=True, server_default="intermediate"),
        sa.Column("is_native", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_languages_profile", "languages", ["profile_id"], schema="career")


def downgrade() -> None:
    """Drop languages table and remove gender column."""
    op.drop_table("languages", schema="career")
    op.drop_column("personal_info", "gender", schema="career")
