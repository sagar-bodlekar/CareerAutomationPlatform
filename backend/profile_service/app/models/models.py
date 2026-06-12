"""SQLAlchemy models for the Profile Service.

All profile tables live under the ``career`` schema in PostgreSQL.
"""

import uuid
from datetime import date, datetime

from shared.database import Base

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship


class UserProfile(Base):
    """Root profile entity — single source of truth for a user's career data."""

    __tablename__ = "user_profiles"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    headline = Column(String(200))
    summary = Column(Text)
    location_city = Column(String(100))
    location_state = Column(String(100))
    location_country = Column(String(100))
    location_type = Column(String(20), default="remote")
    preferred_roles = Column(ARRAY(String), default=list)
    target_salary_min = Column(Integer)
    target_salary_max = Column(Integer)
    target_salary_currency = Column(String(3), default="USD")
    open_to_work = Column(Boolean, default=True)
    open_to_relocation = Column(Boolean, default=False)
    years_of_experience = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    personal_info = relationship(
        "PersonalInfo", back_populates="profile", uselist=False, cascade="all, delete-orphan"
    )
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    work_experiences = relationship(
        "WorkExperience", back_populates="profile", cascade="all, delete-orphan",
        order_by="WorkExperience.start_date.desc().nulls_last()"
    )
    education = relationship(
        "Education", back_populates="profile", cascade="all, delete-orphan"
    )
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship(
        "Certification", back_populates="profile", cascade="all, delete-orphan"
    )
    social_links = relationship(
        "SocialLink", back_populates="profile", cascade="all, delete-orphan"
    )


class PersonalInfo(Base):
    """Personal / contact information."""

    __tablename__ = "personal_info"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("career.user_profiles.id"), nullable=False
    )
    full_name = Column(String(200), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    date_of_birth = Column(Date)
    nationality = Column(String(100))
    pronouns = Column(String(50))
    avatar_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    profile = relationship("UserProfile", back_populates="personal_info")


class Skill(Base):
    """Individual skill with proficiency rating."""

    __tablename__ = "skills"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("career.user_profiles.id"), nullable=False
    )
    name = Column(String(100), nullable=False)
    category = Column(String(100))  # e.g. "Programming Language", "Framework", "Tool"
    proficiency = Column(String(20), default="intermediate")
    years_used = Column(Integer, default=0)
    is_top_skill = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="skills")


class WorkExperience(Base):
    """Work history entry."""

    __tablename__ = "work_experiences"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("career.user_profiles.id"), nullable=False
    )
    company_name = Column(String(200), nullable=False)
    company_url = Column(String(500))
    company_logo_url = Column(String(500))
    job_title = Column(String(200), nullable=False)
    employment_type = Column(String(20), default="full_time")
    location = Column(String(200))
    location_type = Column(String(20))
    start_date = Column(Date, nullable=False)
    start_date_precision = Column(String(10), default="month")
    end_date = Column(Date)
    end_date_precision = Column(String(10), default="month")
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    achievements = Column(ARRAY(String), default=list)
    skills_used = Column(ARRAY(String), default=list)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    profile = relationship("UserProfile", back_populates="work_experiences")


class Education(Base):
    """Education entry."""

    __tablename__ = "education"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("career.user_profiles.id"), nullable=False
    )
    institution = Column(String(200), nullable=False)
    degree = Column(String(200))
    field_of_study = Column(String(200))
    grade = Column(String(50))
    start_date = Column(Date, nullable=False)
    start_date_precision = Column(String(10), default="year")
    end_date = Column(Date)
    end_date_precision = Column(String(10), default="year")
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    activities = Column(ARRAY(String), default=list)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="education")


class Project(Base):
    """Project entry."""

    __tablename__ = "projects"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("career.user_profiles.id"), nullable=False
    )
    name = Column(String(200), nullable=False)
    url = Column(String(500))
    description = Column(Text)
    technologies = Column(ARRAY(String), default=list)
    role = Column(String(200))
    start_date = Column(Date)
    start_date_precision = Column(String(10), default="month")
    end_date = Column(Date)
    end_date_precision = Column(String(10), default="month")
    is_current = Column(Boolean, default=False)
    highlights = Column(ARRAY(String), default=list)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="projects")


class Certification(Base):
    """Certification / license entry."""

    __tablename__ = "certifications"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("career.user_profiles.id"), nullable=False
    )
    name = Column(String(200), nullable=False)
    issuer = Column(String(200))
    url = Column(String(500))
    issue_date = Column(Date)
    expiration_date = Column(Date)
    does_not_expire = Column(Boolean, default=False)
    credential_id = Column(String(200))
    description = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="certifications")


class SocialLink(Base):
    """Social/professional profile link."""

    __tablename__ = "social_links"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(
        UUID(as_uuid=True), ForeignKey("career.user_profiles.id"), nullable=False
    )
    platform = Column(String(50), nullable=False)
    url = Column(String(500), nullable=False)
    label = Column(String(100))
    is_primary = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="social_links")
