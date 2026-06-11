"""Example endpoint implementations for service template."""

from fastapi import APIRouter, Depends, HTTPException
from shared.schemas.common import APIResponse, HealthResponse

from app.api.v1.dependencies import get_service
from app.services.service import ExampleService

router = APIRouter(tags=["example"])


@router.get("/health")
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", service="service-template")


@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    service: ExampleService = Depends(get_service),
) -> APIResponse:
    """Get an item by ID."""
    item = await service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return APIResponse(data=item)
