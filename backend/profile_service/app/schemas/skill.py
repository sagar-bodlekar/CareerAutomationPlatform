"""Skill schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    """Schema for creating a skill."""

    name: str
    category: str | None = None
    proficiency: str = "intermediate"
    years_used: int = 0
    is_top_skill: bool = False
    order: int = 0


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""

    name: str | None = None
    category: str | None = None
    proficiency: str | None = None
    years_used: int | None = None
    is_top_skill: bool | None = None
    order: int | None = None


class SkillResponse(BaseModel):
    """Schema for skill response."""

    id: UUID
    profile_id: UUID
    name: str
    category: str | None = None
    proficiency: str = "intermediate"
    years_used: int = 0
    is_top_skill: bool = False
    order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class SkillBulkCreateRequest(BaseModel):
    """Request body for bulk adding skills."""

    skills: list[SkillCreate] = Field(min_length=1, max_length=100)
