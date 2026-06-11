"""SQLAlchemy models for Auth Service.

All tables live under the ``career`` schema.
"""

import uuid
from datetime import datetime

from shared.database import Base

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class AuthUser(Base):
    """Core user authentication record."""

    __tablename__ = "auth_users"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    oauth_connections = relationship(
        "OAuthConnection", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys = relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )


class OAuthConnection(Base):
    """OAuth provider connection for a user."""

    __tablename__ = "oauth_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("career.auth_users.id"), nullable=False
    )
    provider = Column(String(50), nullable=False)  # "google", "linkedin", "github"
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        {"schema": "career"},
    )

    # Relationships
    user = relationship("AuthUser", back_populates="oauth_connections")


class ApiKey(Base):
    """API key for service-to-service authentication."""

    __tablename__ = "api_keys"
    __table_args__ = {"schema": "career"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("career.auth_users.id"), nullable=False
    )
    key_prefix = Column(String(8), nullable=False)  # First 8 chars of the key
    key_hash = Column(String(255), nullable=False)  # Hashed full key
    name = Column(String(100), nullable=False)
    scopes = Column(String(500))  # Comma-separated scope list
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("AuthUser", back_populates="api_keys")
