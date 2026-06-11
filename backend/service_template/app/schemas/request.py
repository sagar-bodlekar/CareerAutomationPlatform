"""Example request schemas for service template."""

from pydantic import BaseModel, Field


class ExampleCreateRequest(BaseModel):
    """Example create request — replace with actual schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Item name")
    description: str | None = Field(None, max_length=500, description="Item description")


class ExampleUpdateRequest(BaseModel):
    """Example update request — replace with actual schema."""

    name: str | None = Field(None, min_length=1, max_length=200, description="Item name")
    description: str | None = Field(None, max_length=500, description="Item description")
