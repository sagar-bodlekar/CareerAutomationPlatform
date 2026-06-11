"""Common API response schemas used across all services."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Field-level error detail."""

    code: str = Field(..., description="Error code (e.g., VALIDATION_ERROR)")
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Human-readable error message")


class ErrorResponse(BaseModel):
    """Error response envelope."""

    success: bool = False
    data: None = None
    errors: list[ErrorDetail] = Field(default_factory=list)


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    success: bool = True
    data: T | None = None
    errors: list[ErrorDetail] | None = None
    meta: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    service: str = "unknown"
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
