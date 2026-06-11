"""Health check for job service."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "job-service",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
