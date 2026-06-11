"""Application service models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from shared.database import Base


class Application(Base):
    """Job application record with state machine tracking."""

    __tablename__ = "applications"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, nullable=False, index=True)
    job_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)

    # ─── State ────────────────────────────────────────────
    status = Column(String(30), default="draft", nullable=False, index=True)
    previous_status = Column(String(30), nullable=True)

    # ─── Package ──────────────────────────────────────────
    resume_id = Column(Integer, nullable=True, comment="Resume ID from Resume Service")
    resume_file_id = Column(Integer, nullable=True, comment="PDF file ID")
    cover_letter_id = Column(Integer, nullable=True, comment="Cover letter content ID")
    email_id = Column(Integer, nullable=True, comment="Email content ID")
    package_data = Column(JSONB, nullable=True, comment="Full application package metadata")

    # ─── Job Info (cached) ────────────────────────────────
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    job_location = Column(String(255), nullable=True)
    job_url = Column(String(1000), nullable=True)

    # ─── Delivery ─────────────────────────────────────────
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivery_status = Column(String(30), nullable=True, comment="pending, sent, delivered, bounced")
    delivery_message_id = Column(String(255), nullable=True, comment="Provider message ID")
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)

    # ─── Scoring ──────────────────────────────────────────
    match_score = Column(Float, nullable=True, comment="Match score at time of application")
    match_id = Column(Integer, nullable=True, comment="Match record ID")

    # ─── Notes ────────────────────────────────────────────
    notes = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=True)

    # ─── Timestamps ───────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ApplicationEvent(Base):
    """Audit trail of application state changes."""

    __tablename__ = "application_events"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("career.applications.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)
    event_type = Column(String(50), nullable=False, comment="status_change, note_added, email_sent, etc.")
    description = Column(Text, nullable=True)
    actor = Column(String(50), default="system", comment="system, user, ai, webhook")
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
