"""API router aggregation."""

from fastapi import APIRouter

from app.api.v1 import endpoints as v1_endpoints
from app.api.v1.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(v1_endpoints.router)
