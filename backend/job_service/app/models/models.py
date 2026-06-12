"""Job service SQLAlchemy models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from shared.database import Base

from ..models.enums import (
    EmploymentType,
    ExperienceLevel,
    JobStatus,
    LocationType,
    SalaryCurrency,
    SourceType,
)


def _enum_values(enum_cls):
    """Return enum member values for SQLAlchemy Enum type."""
    return [e.value for e in enum_cls]


class Job(Base):
    """Normalized job posting from any source."""

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_required_skills_gin", "required_skills", postgresql_using="gin"),
        Index("ix_jobs_nice_to_have_skills_gin", "nice_to_have_skills", postgresql_using="gin"),
        Index("ix_jobs_source_external", "source_id", "external_id", unique=True),
        Index("ix_jobs_title_company", "title", "company_name"),
        Index("ix_jobs_status_posted", "status", "posted_at"),
        {"schema": "career"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), nullable=True, comment="ID from source system")
    source_id = Column(Integer, ForeignKey("career.job_sources.id", ondelete="SET NULL"), nullable=True)

    # ─── Core fields ────────────────────────────────────────
    title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    company_description = Column(Text, nullable=True)
    company_url = Column(String(500), nullable=True)
    company_logo = Column(String(500), nullable=True)

    # ─── Location ───────────────────────────────────────────
    location = Column(String(255), nullable=True)
    location_type = Column(Enum(LocationType, name="location_type", schema="career", values_callable=_enum_values), nullable=True)
    is_remote = Column(Integer, default=0, comment="Boolean flag")
    remote_type = Column(String(50), nullable=True, comment="Fully remote, hybrid, onsite")

    # ─── Details ────────────────────────────────────────────
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    required_skills = Column(ARRAY(String(100)), nullable=True, comment="Extracted skill keywords")
    nice_to_have_skills = Column(ARRAY(String(100)), nullable=True)

    # ─── Experience & Education ─────────────────────────────
    experience_min_years = Column(Integer, nullable=True)
    experience_max_years = Column(Integer, nullable=True)
    experience_level = Column(Enum(ExperienceLevel, name="experience_level", schema="career", values_callable=_enum_values), nullable=True)
    education_required = Column(String(255), nullable=True)
    degree_preferred = Column(String(255), nullable=True)

    # ─── Compensation ───────────────────────────────────────
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(Enum(SalaryCurrency, name="salary_currency", schema="career", values_callable=_enum_values), nullable=True)
    salary_period = Column(String(20), nullable=True, comment="yearly, monthly, hourly")
    salary_visible = Column(Integer, default=0, comment="Boolean flag")

    # ─── Employment ─────────────────────────────────────────
    employment_type = Column(Enum(EmploymentType, name="employment_type", schema="career", values_callable=_enum_values), nullable=True)
    industry = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)

    # ─── Meta ───────────────────────────────────────────────
    job_url = Column(String(1000), nullable=True, comment="Original job posting URL")
    apply_url = Column(String(1000), nullable=True)
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Enum(JobStatus, name="job_status", schema="career", values_callable=_enum_values), default=JobStatus.ACTIVE, nullable=False)
    raw_data = Column(JSONB, nullable=True, comment="Original scraped JSON for audit")

    # ─── Enrichment ─────────────────────────────────────────
    skills_embedding = Column(ARRAY(Float), nullable=True, comment="Vector embedding of required_skills")
    normalized_title = Column(String(255), nullable=True, comment="Canonical job title")
    company_id_normalized = Column(String(100), nullable=True, comment="Normalized company identifier")
    enriched_at = Column(DateTime(timezone=True), nullable=True)

    # ─── Timestamps ─────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class JobSource(Base):
    """Configured job source for scraping."""

    __tablename__ = "job_sources"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment="Source name (e.g., remoteok, linkedin)")
    source_type = Column(Enum(SourceType, name="source_type", schema="career", values_callable=_enum_values), nullable=False)
    display_name = Column(String(255), nullable=False, comment="Human-readable name")
    base_url = Column(String(500), nullable=False, comment="Base URL for scraping")
    api_url = Column(String(500), nullable=True, comment="API endpoint if applicable")
    api_key_required = Column(Integer, default=0, comment="Boolean flag")
    is_active = Column(Integer, default=1, comment="Whether this source is actively scraped")
    scrape_interval_minutes = Column(Integer, default=60, comment="How often to scrape")
    config = Column(JSONB, nullable=True, comment="Source-specific configuration (headers, selectors, etc.)")
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    last_scrape_status = Column(String(50), nullable=True, comment="success, failed, partial")
    last_scrape_count = Column(Integer, nullable=True, comment="Jobs found in last scrape")
    error_count = Column(Integer, default=0, comment="Consecutive scrape failures")
    priority = Column(Integer, default=100, comment="Scrape priority (lower = higher)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
