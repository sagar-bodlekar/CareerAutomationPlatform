"""Health check endpoint for Profile Service."""

from fastapi import APIRouter
from shared.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", service="profile-service")
