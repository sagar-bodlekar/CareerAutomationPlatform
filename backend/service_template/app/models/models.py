"""Example SQLAlchemy model for service template."""

import uuid
from datetime import datetime

from shared.database import Base

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID


class ExampleItem(Base):
    """Example model — replace with actual models."""

    __tablename__ = "example_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
