"""Create profile tables (user_profiles, personal_info, skills, work_experiences, education, projects, certifications, social_links)

Revision ID: 001_create_profile_tables
Revises: None
Create Date: 2026-06-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_profile_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all profile tables under career schema."""

    # Create career schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS career")

    # ─── user_profiles ──────────────────────────────────────
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True, unique=True),
        sa.Column("headline", sa.String(200), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("location_city", sa.String(100), nullable=True),
        sa.Column("location_state", sa.String(100), nullable=True),
        sa.Column("location_country", sa.String(100), nullable=True),
        sa.Column("location_type", sa.String(20), nullable=True),
        sa.Column("preferred_roles", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("target_salary_min", sa.Integer(), nullable=True),
        sa.Column("target_salary_max", sa.Integer(), nullable=True),
        sa.Column("target_salary_currency", sa.String(3), nullable=True, server_default="USD"),
        sa.Column("open_to_work", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("open_to_relocation", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("years_of_experience", sa.Float(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        schema="career",
    )

    # ─── personal_info ──────────────────────────────────────
    op.create_table(
        "personal_info",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address_line1", sa.String(255), nullable=True),
        sa.Column("address_line2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("pronouns", sa.String(50), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        schema="career",
    )

    # ─── skills ─────────────────────────────────────────────
    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("proficiency", sa.String(20), nullable=True, server_default="intermediate"),
        sa.Column("years_used", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("is_top_skill", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_skills_profile_category", "skills", ["profile_id", "category"], schema="career")

    # ─── work_experiences ───────────────────────────────────
    op.create_table(
        "work_experiences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("company_url", sa.String(500), nullable=True),
        sa.Column("company_logo_url", sa.String(500), nullable=True),
        sa.Column("job_title", sa.String(200), nullable=False),
        sa.Column("employment_type", sa.String(20), nullable=True, server_default="full_time"),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("location_type", sa.String(20), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("start_date_precision", sa.String(10), nullable=True, server_default="month"),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("end_date_precision", sa.String(10), nullable=True, server_default="month"),
        sa.Column("is_current", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("achievements", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("skills_used", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_work_experiences_profile_dates", "work_experiences", ["profile_id", "start_date"], schema="career")

    # ─── education ──────────────────────────────────────────
    op.create_table(
        "education",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("institution", sa.String(200), nullable=False),
        sa.Column("degree", sa.String(200), nullable=True),
        sa.Column("field_of_study", sa.String(200), nullable=True),
        sa.Column("grade", sa.String(50), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("start_date_precision", sa.String(10), nullable=True, server_default="year"),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("end_date_precision", sa.String(10), nullable=True, server_default="year"),
        sa.Column("is_current", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("activities", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_education_profile", "education", ["profile_id"], schema="career")

    # ─── projects ───────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("technologies", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("role", sa.String(200), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("start_date_precision", sa.String(10), nullable=True, server_default="month"),
        sa.Column("end_date_precision", sa.String(10), nullable=True, server_default="month"),
        sa.Column("is_current", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("highlights", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="career",
    )

    # ─── certifications ─────────────────────────────────────
    op.create_table(
        "certifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("issuer", sa.String(200), nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("expiration_date", sa.Date(), nullable=True),
        sa.Column("does_not_expire", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("credential_id", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_certifications_profile", "certifications", ["profile_id"], schema="career")

    # ─── social_links ───────────────────────────────────────
    op.create_table(
        "social_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("career.user_profiles.id"), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("label", sa.String(100), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        schema="career",
    )
    op.create_index("ix_social_links_profile", "social_links", ["profile_id"], schema="career")


def downgrade() -> None:
    """Drop all profile tables."""
    op.drop_table("social_links", schema="career")
    op.drop_table("certifications", schema="career")
    op.drop_table("projects", schema="career")
    op.drop_table("education", schema="career")
    op.drop_table("work_experiences", schema="career")
    op.drop_table("skills", schema="career")
    op.drop_table("personal_info", schema="career")
    op.drop_table("user_profiles", schema="career")
