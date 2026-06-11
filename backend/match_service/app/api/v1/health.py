"""Health check for match service."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "match-service",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
