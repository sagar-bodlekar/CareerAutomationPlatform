"""Health check for AI orchestrator."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "ai-orchestrator",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
