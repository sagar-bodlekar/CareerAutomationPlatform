"""Match service models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from shared.database import Base


class JobMatch(Base):
    """Match result between a user profile and a job posting."""

    __tablename__ = "job_matches"
    __table_args__ = {"schema": "career"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, nullable=False, index=True, comment="User profile ID")
    job_id = Column(Integer, nullable=False, index=True, comment="Job ID from Job Service")

    # ─── Scores (0-100) ─────────────────────────────────────
    overall_score = Column(Float, nullable=False, default=0.0, comment="Overall match score 0-100")
    skills_score = Column(Float, nullable=True, comment="Skills match score 0-100")
    experience_score = Column(Float, nullable=True, comment="Experience match score 0-100")
    education_score = Column(Float, nullable=True, comment="Education match score 0-100")
    location_score = Column(Float, nullable=True, comment="Location match score 0-100")
    title_score = Column(Float, nullable=True, comment="Title similarity score 0-100")

    # ─── Match Details ──────────────────────────────────────
    matched_skills = Column(JSONB, nullable=True, comment="List of matched skill keywords")
    missing_skills = Column(JSONB, nullable=True, comment="List of missing skill keywords")
    extra_skills = Column(JSONB, nullable=True, comment="Skills candidate has but job doesn't require")
    skill_gaps = Column(JSONB, nullable=True, comment="Detailed skill gap analysis")
    match_summary = Column(Text, nullable=True, comment="Human-readable match summary")

    # ─── AI Enhancement ─────────────────────────────────────
    ai_enhanced = Column(Integer, default=0, comment="Whether AI was used to enhance scoring")
    ai_recommendation = Column(Text, nullable=True, comment="AI-generated recommendation text")
    ai_match_data = Column(JSONB, nullable=True, comment="Full AI match analysis response")

    # ─── Ranking ────────────────────────────────────────────
    rank = Column(Integer, nullable=True, comment="Rank among matches for this profile")
    is_top_match = Column(Integer, default=0, comment="Whether this is in top-N matches")

    # ─── Status ─────────────────────────────────────────────
    status = Column(String(20), default="active", comment="active, archived, applied")
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)

    # ─── Timestamps ─────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ─── Indexes ────────────────────────────────────────────
    __table_args__ = (
        # TODO: Add indexes after creating the table schema
        # Index("ix_job_matches_profile_score", "profile_id", "overall_score"),
        # Index("ix_job_matches_job_profile", "job_id", "profile_id", unique=True),
        {"schema": "career"},
    )
