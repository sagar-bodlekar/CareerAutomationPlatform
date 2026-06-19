"""Tracking service models for analytics and statistics."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from shared.database import Base


# ── Read-Only Application Model ─────────────────────────────────
# Maps to the existing career.applications table from application_service.


class Application(Base):
    """Read-only reference to the applications table."""

    __tablename__ = "applications"
    __table_args__ = {"schema": "career", "extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_id = Column(Integer, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    status = Column(String(30), default="draft", nullable=False, index=True)
    previous_status = Column(String(30), nullable=True)
    resume_id = Column(Integer, nullable=True)
    resume_file_id = Column(Integer, nullable=True)
    cover_letter_id = Column(Integer, nullable=True)
    email_id = Column(Integer, nullable=True)
    package_data = Column(JSONB, nullable=True)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    job_location = Column(String(255), nullable=True)
    job_url = Column(String(1000), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivery_status = Column(String(30), nullable=True)
    delivery_message_id = Column(String(255), nullable=True)
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    match_score = Column(Float, nullable=True)
    match_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ApplicationStat(Base):
    """Aggregated application statistics per user/profile."""

    __tablename__ = "application_stats"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    total_applications = Column(Integer, default=0)
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_replied = Column(Integer, default=0)
    total_interviews = Column(Integer, default=0)
    total_offers = Column(Integer, default=0)
    total_rejected = Column(Integer, default=0)
    avg_match_score = Column(Float, nullable=True)
    avg_response_time_hours = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True, comment="Percentage of sent that led to interviews")
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ApplicationFunnel(Base):
    """Funnel snapshot for application status distribution."""

    __tablename__ = "application_funnels"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status_counts = Column(JSONB, nullable=False, comment="Map of status -> count")
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DailyCount(Base):
    """Daily application counts for trend analysis."""

    __tablename__ = "daily_application_counts"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    count = Column(Integer, default=0, nullable=False)
    sent_count = Column(Integer, default=0)
    interview_count = Column(Integer, default=0)
    offer_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
