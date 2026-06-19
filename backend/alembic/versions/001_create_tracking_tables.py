"""Create tracking service tables with UUID profile_id columns.

If tables already exist (from create_all during development), their
profile_id columns are migrated from Integer to UUID.

Revision ID: 001_create_tracking_tables
Revises: 002_profile_id_to_uuid
Create Date: 2026-06-19
"""
from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_create_tracking_tables"
down_revision: Optional[str] = "002_profile_id_to_uuid"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None

SCHEMA = "career"


def _table_exists(table_name: str) -> bool:
    """Check if a table exists in the career schema."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_schema = :schema AND table_name = :table)"
        ),
        {"schema": SCHEMA, "table": table_name},
    )
    return result.scalar()


def _column_type(table: str, column: str) -> str | None:
    """Get the data type of a column, or None if table/column doesn't exist."""
    if not _table_exists(table):
        return None
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table AND column_name = :col"
        ),
        {"schema": SCHEMA, "table": table, "col": column},
    )
    row = result.fetchone()
    return row[0] if row else None


def _migrate_column_to_uuid(table: str, column: str, nullable: bool = False) -> None:
    """Migrate a column from Integer to UUID. Assumes table already exists."""
    current_type = _column_type(table, column)
    if current_type == "uuid":
        return  # Already UUID — nothing to do

    # Drop old index for this column
    idx_name = f"ix_{table}_{column}"
    op.drop_index(idx_name, table_name=table, schema=SCHEMA, if_exists=True)

    if current_type != "uuid":
        # Integer → UUID: drop column, add UUID column, backfill
        op.drop_column(table, column, schema=SCHEMA)
        op.add_column(
            table,
            sa.Column(column, postgresql.UUID(as_uuid=True), nullable=True),
            schema=SCHEMA,
        )
        op.execute(
            f"UPDATE {SCHEMA}.{table} SET {column} = gen_random_uuid() "
            f"WHERE {column} IS NULL"
        )
        if not nullable:
            op.execute(
                f"ALTER TABLE {SCHEMA}.{table} ALTER COLUMN {column} SET NOT NULL"
            )

    # Recreate index
    op.create_index(idx_name, table, [column], schema=SCHEMA, if_not_exists=True)


def upgrade() -> None:
    """Create or migrate tracking service tables with UUID profile_id columns."""

    # ── application_stats ──────────────────────────────────────
    if not _table_exists("application_stats"):
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
            schema=SCHEMA,
        )
    else:
        _migrate_column_to_uuid("application_stats", "profile_id", nullable=False)

    op.create_index(
        "ix_application_stats_profile_id", "application_stats", ["profile_id"],
        schema=SCHEMA, if_not_exists=True,
    )

    # ── application_funnels ────────────────────────────────────
    if not _table_exists("application_funnels"):
        op.create_table(
            "application_funnels",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("status_counts", postgresql.JSONB(), nullable=False),
            sa.Column("snapshot_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            schema=SCHEMA,
        )
    else:
        _migrate_column_to_uuid("application_funnels", "profile_id", nullable=False)

    op.create_index(
        "ix_application_funnels_profile_id", "application_funnels", ["profile_id"],
        schema=SCHEMA, if_not_exists=True,
    )
    op.create_index(
        "ix_application_funnels_snapshot_date", "application_funnels", ["snapshot_date"],
        schema=SCHEMA, if_not_exists=True,
    )

    # ── daily_application_counts ───────────────────────────────
    if not _table_exists("daily_application_counts"):
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
            schema=SCHEMA,
        )
    else:
        _migrate_column_to_uuid("daily_application_counts", "profile_id", nullable=False)

    op.create_index(
        "ix_daily_counts_profile_id", "daily_application_counts", ["profile_id"],
        schema=SCHEMA, if_not_exists=True,
    )
    op.create_index(
        "ix_daily_counts_date", "daily_application_counts", ["date"],
        schema=SCHEMA, if_not_exists=True,
    )


def downgrade() -> None:
    """Drop all tracking service tables."""
    op.drop_table("daily_application_counts", schema=SCHEMA)
    op.drop_table("application_funnels", schema=SCHEMA)
    op.drop_table("application_stats", schema=SCHEMA)
