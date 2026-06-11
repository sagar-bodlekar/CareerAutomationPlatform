"""SQLAlchemy models for Resume Service.

All tables live under the ``career`` schema.
"""

import uuid
from datetime import datetime

from shared.database import Base

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class ResumeTemplate(Base):
    """A named resume template with HTML/CSS content."""

    __tablename__ = "resume_templates"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    html_content = Column(Text, nullable=False)
    css_content = Column(Text)
    thumbnail_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="template")


class Resume(Base):
    """A user's master resume generated from their profile data.

    Contains structured JSON content that can be rendered into
    role-specific versions and exported to PDF.
    """

    __tablename__ = "resumes"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    profile_id = Column(UUID(as_uuid=True), nullable=False)
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("career.resume_templates.id"), nullable=True
    )
    title = Column(String(200), default="Master Resume")
    # Structured resume content stored as JSONB
    content = Column(JSONB, default=dict)
    # Role-specific version metadata
    target_role = Column(String(200))
    target_job_id = Column(UUID(as_uuid=True))
    ats_score = Column(Float)
    ats_score_breakdown = Column(JSONB)
    is_master = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("ResumeTemplate", back_populates="resumes")
    files = relationship("ResumeFile", back_populates="resume", cascade="all, delete-orphan")


class ResumeFile(Base):
    """Generated PDF file metadata for a resume."""

    __tablename__ = "resume_files"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(
        UUID(as_uuid=True), ForeignKey("career.resumes.id"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer)
    content_type = Column(String(100), default="application/pdf")
    minio_bucket = Column(String(100), nullable=False)
    minio_object_key = Column(String(500), nullable=False)
    minio_presigned_url = Column(String(1000))
    presigned_url_expires_at = Column(DateTime)
    page_count = Column(Integer)
    is_optimized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="files")
