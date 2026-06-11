"""Create job and job_source tables.

Revision ID: 001_create_job_tables
Revises: 001_create_resume_tables
Create Date: 2026-06-11
"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_job_tables"
down_revision: Optional[str] = "001_create_resume_tables"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    """Create job and job_source tables."""

    # Create enums in career schema
    op.execute("CREATE SCHEMA IF NOT EXISTS career")

    # ─── Enums ──────────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE career.employment_type AS ENUM (
                'full_time', 'part_time', 'contract', 'temporary',
                'internship', 'freelance', 'other'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE career.job_status AS ENUM (
                'active', 'filled', 'expired', 'draft', 'closed'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE career.salary_currency AS ENUM (
                'USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD', 'JPY', 'CNY', 'OTHER'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE career.source_type AS ENUM (
                'api', 'rss', 'scrape', 'manual', 'aggregator'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE career.location_type AS ENUM (
                'remote', 'onsite', 'hybrid'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE career.experience_level AS ENUM (
                'entry', 'mid', 'senior', 'lead', 'executive'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # ─── JobSources table ─────────────────────────────────────
    op.create_table(
        "job_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("source_type", postgresql.ENUM("api", "rss", "scrape", "manual", "aggregator", name="source_type", schema="career"), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=False),
        sa.Column("api_url", sa.String(500), nullable=True),
        sa.Column("api_key_required", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("scrape_interval_minutes", sa.Integer(), server_default=sa.text("60"), nullable=False),
        sa.Column("config", postgresql.JSONB(), nullable=True),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_scrape_status", sa.String(50), nullable=True),
        sa.Column("last_scrape_count", sa.Integer(), nullable=True),
        sa.Column("error_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("priority", sa.Integer(), server_default=sa.text("100"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="career",
    )

    # ─── Jobs table ───────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("company_description", sa.Text(), nullable=True),
        sa.Column("company_url", sa.String(500), nullable=True),
        sa.Column("company_logo", sa.String(500), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("location_type", postgresql.ENUM("remote", "onsite", "hybrid", name="location_type", schema="career"), nullable=True),
        sa.Column("is_remote", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("remote_type", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("required_skills", postgresql.ARRAY(sa.String(100)), nullable=True),
        sa.Column("nice_to_have_skills", postgresql.ARRAY(sa.String(100)), nullable=True),
        sa.Column("experience_min_years", sa.Integer(), nullable=True),
        sa.Column("experience_max_years", sa.Integer(), nullable=True),
        sa.Column("experience_level", postgresql.ENUM("entry", "mid", "senior", "lead", "executive", name="experience_level", schema="career"), nullable=True),
        sa.Column("education_required", sa.String(255), nullable=True),
        sa.Column("degree_preferred", sa.String(255), nullable=True),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("salary_currency", postgresql.ENUM("USD", "EUR", "GBP", "INR", "CAD", "AUD", "JPY", "CNY", "OTHER", name="salary_currency", schema="career"), nullable=True),
        sa.Column("salary_period", sa.String(20), nullable=True),
        sa.Column("salary_visible", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("employment_type", postgresql.ENUM("full_time", "part_time", "contract", "temporary", "internship", "freelance", "other", name="employment_type", schema="career"), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("function", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("job_url", sa.String(1000), nullable=True),
        sa.Column("apply_url", sa.String(1000), nullable=True),
        sa.Column("application_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", postgresql.ENUM("active", "filled", "expired", "draft", "closed", name="job_status", schema="career"), server_default=sa.text("'active'"), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(), nullable=True),
        sa.Column("skills_embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("normalized_title", sa.String(255), nullable=True),
        sa.Column("company_id_normalized", sa.String(100), nullable=True),
        sa.Column("enriched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["career.job_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="career",
    )

    # ─── Indexes ──────────────────────────────────────────────
    op.create_index("ix_jobs_title", "jobs", ["title"], schema="career")
    op.create_index("ix_jobs_company_name", "jobs", ["company_name"], schema="career")
    op.create_index("ix_jobs_required_skills_gin", "jobs", ["required_skills"], schema="career", postgresql_using="gin")
    op.create_index("ix_jobs_nice_to_have_skills_gin", "jobs", ["nice_to_have_skills"], schema="career", postgresql_using="gin")
    op.create_index("ix_jobs_source_external", "jobs", ["source_id", "external_id"], schema="career", unique=True)
    op.create_index("ix_jobs_title_company", "jobs", ["title", "company_name"], schema="career")
    op.create_index("ix_jobs_status_posted", "jobs", ["status", "posted_at"], schema="career")


def downgrade() -> None:
    """Drop job and job_source tables."""
    op.drop_table("jobs", schema="career")
    op.drop_table("job_sources", schema="career")

    op.execute("DROP TYPE IF EXISTS career.employment_type")
    op.execute("DROP TYPE IF EXISTS career.job_status")
    op.execute("DROP TYPE IF EXISTS career.salary_currency")
    op.execute("DROP TYPE IF EXISTS career.source_type")
    op.execute("DROP TYPE IF EXISTS career.location_type")
    op.execute("DROP TYPE IF EXISTS career.experience_level")
