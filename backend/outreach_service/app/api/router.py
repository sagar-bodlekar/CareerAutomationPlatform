"""API router aggregation."""

from fastapi import APIRouter

from app.api.v1 import endpoints as v1_endpoints

api_router = APIRouter()
api_router.include_router(v1_endpoints.router, prefix="/v1")
