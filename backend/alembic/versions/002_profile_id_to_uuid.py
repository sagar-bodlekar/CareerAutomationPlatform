"""Change profile_id and user_id from Integer to UUID.

Revision ID: 002_profile_id_to_uuid
Revises: 001_create_application_tables
Create Date: 2026-06-19
"""
from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_profile_id_to_uuid"
down_revision: Optional[str] = "001_create_application_tables"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    """Migrate profile_id and user_id from Integer to UUID.

    Strategy:
    1. Drop existing indexes on the old columns
    2. Drop old Integer columns
    3. Add new UUID columns as nullable
    4. Backfill existing rows with random UUIDs
    5. Set NOT NULL constraint on profile_id
    6. Recreate indexes
    """
    schema = "career"

    # --- profile_id: Integer → UUID ---
    op.drop_index("ix_applications_profile_id", table_name="applications", schema=schema)
    op.drop_index("ix_applications_profile_status", table_name="applications", schema=schema)
    op.drop_column("applications", "profile_id", schema=schema)
    op.add_column(
        "applications",
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema=schema,
    )
    # Backfill existing rows (if any) with generated UUIDs
    op.execute(
        "UPDATE career.applications SET profile_id = gen_random_uuid() "
        "WHERE profile_id IS NULL"
    )
    # Now safe to set NOT NULL
    op.execute(
        "ALTER TABLE career.applications ALTER COLUMN profile_id SET NOT NULL"
    )
    op.create_index("ix_applications_profile_id", "applications", ["profile_id"], schema=schema)
    op.create_index(
        "ix_applications_profile_status",
        "applications",
        ["profile_id", "status"],
        schema=schema,
    )

    # --- user_id: Integer → UUID ---
    op.drop_index("ix_applications_user_id", table_name="applications", schema=schema)
    op.drop_column("applications", "user_id", schema=schema)
    op.add_column(
        "applications",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema=schema,
    )
    op.execute(
        "UPDATE career.applications SET user_id = gen_random_uuid() "
        "WHERE user_id IS NULL"
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"], schema=schema)


def downgrade() -> None:
    """Revert UUID columns back to Integer."""
    schema = "career"

    # --- profile_id: UUID → Integer ---
    op.drop_index("ix_applications_profile_id", table_name="applications", schema=schema)
    op.drop_index("ix_applications_profile_status", table_name="applications", schema=schema)
    op.drop_column("applications", "profile_id", schema=schema)
    op.add_column(
        "applications",
        sa.Column("profile_id", sa.Integer(), nullable=False),
        schema=schema,
    )
    op.create_index("ix_applications_profile_id", "applications", ["profile_id"], schema=schema)
    op.create_index(
        "ix_applications_profile_status",
        "applications",
        ["profile_id", "status"],
        schema=schema,
    )

    # --- user_id: UUID → Integer ---
    op.drop_index("ix_applications_user_id", table_name="applications", schema=schema)
    op.drop_column("applications", "user_id", schema=schema)
    op.add_column(
        "applications",
        sa.Column("user_id", sa.Integer(), nullable=True),
        schema=schema,
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"], schema=schema)
