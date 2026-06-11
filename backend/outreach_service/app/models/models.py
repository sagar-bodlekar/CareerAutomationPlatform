"""Outreach service models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from shared.database import Base


class OutreachContent(Base):
    """Stores generated outreach content (cover letters, emails) with versioning."""

    __tablename__ = "outreach_content"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String(20), nullable=False, comment="cover_letter or email")
    profile_id = Column(Integer, nullable=True, index=True)
    job_id = Column(Integer, nullable=True, index=True)
    application_id = Column(Integer, nullable=True, index=True)

    # ─── Content ─────────────────────────────────────────
    subject = Column(String(500), nullable=True, comment="Email subject line")
    body = Column(Text, nullable=False, comment="Generated content body")
    tone = Column(String(50), default="professional", comment="professional, enthusiastic, concise")
    target_role = Column(String(255), nullable=True)

    # ─── AI Generation ───────────────────────────────────
    ai_agent_used = Column(String(100), nullable=True, comment="AI agent name if AI-generated")
    ai_execution_id = Column(Integer, nullable=True, comment="AI execution log ID")
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # ─── Versioning ──────────────────────────────────────
    version = Column(Integer, default=1, nullable=False)
    parent_version_id = Column(Integer, nullable=True, comment="Previous version ID")
    edit_count = Column(Integer, default=0, nullable=False)

    # ─── Personalization ─────────────────────────────────
    recipient_name = Column(String(255), nullable=True)
    recipient_role = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    personalization_hooks = Column(JSONB, nullable=True)

    # ─── Metadata ────────────────────────────────────────
    status = Column(String(20), default="draft", comment="draft, finalized, sent")
    is_template = Column(Integer, default=0, comment="Whether this can be used as a template")
    template_name = Column(String(255), nullable=True)
    tags = Column(JSONB, nullable=True)

    # ─── Timestamps ──────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
