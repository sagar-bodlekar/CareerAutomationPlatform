"""Application service API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from shared.schemas.common import APIResponse

from ...schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from ...schemas.event import ApplicationEventResponse
from ...services.application_service import ApplicationService
from .dependencies import get_application_service, get_current_user_id

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=APIResponse[ApplicationResponse], status_code=201)
async def create_application(
    data: ApplicationCreate,
    svc: ApplicationService = Depends(get_application_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Create a new application draft."""
    app = await svc.create(data)
    return APIResponse(data=ApplicationResponse.model_validate(app))


@router.get("/{application_id}", response_model=APIResponse[ApplicationResponse])
async def get_application(
    application_id: int,
    svc: ApplicationService = Depends(get_application_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Get application with timeline and state info."""
    app = await svc.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    events = await svc.get_events(application_id)
    return APIResponse(data=app.model_dump() | {"events": [ApplicationEventResponse.model_validate(e) for e in events]})


@router.patch("/{application_id}/status", response_model=APIResponse[ApplicationResponse])
async def update_application_status(
    application_id: int,
    update: ApplicationUpdate,
    svc: ApplicationService = Depends(get_application_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Update application status (with state machine validation)."""
    try:
        app = await svc.update(application_id, update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return APIResponse(data=app)


@router.post("/{application_id}/submit", response_model=APIResponse[ApplicationResponse])
async def submit_application(
    application_id: int,
    svc: ApplicationService = Depends(get_application_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Submit an application (transitions to sent)."""
    try:
        app = await svc.submit(application_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return APIResponse(data=app)


@router.get("", response_model=APIResponse)
async def list_applications(
    profile_id: str = Query(..., description="Profile ID"),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    svc: ApplicationService = Depends(get_application_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """List applications with filters and pagination."""
    apps, total = await svc.list_applications(profile_id, page=page, per_page=per_page, status=status)
    return APIResponse(data={"applications": [a.model_dump() for a in apps], "total": total, "page": page, "per_page": per_page})


@router.get("/{application_id}/events", response_model=APIResponse)
async def get_application_events(
    application_id: int,
    svc: ApplicationService = Depends(get_application_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Get application event timeline."""
    events = await svc.get_events(application_id)
    return APIResponse(data=[ApplicationEventResponse.model_validate(e) for e in events])
