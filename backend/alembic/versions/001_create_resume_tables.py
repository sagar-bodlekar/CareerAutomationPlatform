"""Create resume tables (resumes, resume_files, resume_templates)

Revision ID: 001_create_resume_tables
Revises: 001_create_auth_tables
Create Date: 2026-06-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_resume_tables"
down_revision: Union[str, None] = "001_create_auth_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create resume tables under career schema."""

    # ─── resume_templates ────────────────────────────────────
    op.create_table(
        "resume_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("html_content", sa.Text(), nullable=False),
        sa.Column("css_content", sa.Text(), nullable=True),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("is_default", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        schema="career",
    )

    # ─── resumes ─────────────────────────────────────────────
    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("career.resume_templates.id"), nullable=True),
        sa.Column("title", sa.String(200), nullable=True, server_default="Master Resume"),
        sa.Column("content", postgresql.JSONB(), nullable=True, server_default="{}"),
        sa.Column("target_role", sa.String(200), nullable=True),
        sa.Column("target_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ats_score", sa.Float(), nullable=True),
        sa.Column("ats_score_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("is_master", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("version", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"], schema="career")
    op.create_index("ix_resumes_user_active", "resumes", ["user_id", "is_deleted"], schema="career")

    # ─── resume_files ────────────────────────────────────────
    op.create_table(
        "resume_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("career.resumes.id"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("content_type", sa.String(100), nullable=True, server_default="application/pdf"),
        sa.Column("minio_bucket", sa.String(100), nullable=False),
        sa.Column("minio_object_key", sa.String(500), nullable=False),
        sa.Column("minio_presigned_url", sa.String(1000), nullable=True),
        sa.Column("presigned_url_expires_at", sa.DateTime(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("is_optimized", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_resume_files_resume_id", "resume_files", ["resume_id"], schema="career")


def downgrade() -> None:
    """Drop all resume tables."""
    op.drop_table("resume_files", schema="career")
    op.drop_table("resumes", schema="career")
    op.drop_table("resume_templates", schema="career")
