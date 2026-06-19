"""Tracking service API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from shared.schemas.common import APIResponse

from ...schemas.tracking import TrackingStats
from ...schemas.analytics import AnalyticsResponse
from ...services.tracking_service import TrackingService
from ...services.analytics_service import AnalyticsService
from ...services.export_service import ExportService
from .dependencies import get_tracking_service, get_analytics_service, get_export_service, get_current_user_id

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.get("/stats", response_model=APIResponse[TrackingStats])
async def get_tracking_stats(
    profile_id: str = Query(..., description="Profile ID"),
    svc: TrackingService = Depends(get_tracking_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Get aggregate tracking statistics for a profile."""
    stats = await svc.get_stats(profile_id)
    return APIResponse(data=stats)


@router.get("/analytics", response_model=APIResponse[AnalyticsResponse])
async def get_analytics(
    profile_id: str = Query(..., description="Profile ID"),
    svc: AnalyticsService = Depends(get_analytics_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Get detailed analytics including funnel and daily trends."""
    analytics = await svc.get_analytics(profile_id)
    return APIResponse(data=analytics)


@router.get("/funnel", response_model=APIResponse)
async def get_funnel(
    profile_id: str = Query(..., description="Profile ID"),
    svc: TrackingService = Depends(get_tracking_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Get application funnel data (status distribution)."""
    funnel = await svc.get_funnel(profile_id)
    return APIResponse(data=[f.model_dump() for f in funnel])


@router.get("/trends", response_model=APIResponse)
async def get_daily_trends(
    profile_id: str = Query(..., description="Profile ID"),
    days: int = Query(30, ge=1, le=365),
    svc: TrackingService = Depends(get_tracking_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Get daily application trends."""
    trends = await svc.get_daily_trends(profile_id, days=days)
    return APIResponse(data=[t.model_dump() for t in trends])


@router.get("/applications", response_model=APIResponse)
async def list_applications(
    profile_id: str = Query(..., description="Profile ID"),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|sent_at|match_score|company_name)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    svc: TrackingService = Depends(get_tracking_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """List applications with sorting and filtering for tracking."""
    apps, total = await svc.get_applications_list(
        profile_id, status=status, page=page, per_page=per_page,
        sort_by=sort_by, sort_order=sort_order,
    )
    return APIResponse(data={
        "applications": [{
            "id": a.id,
            "job_title": a.job_title,
            "company_name": a.company_name,
            "status": a.status,
            "match_score": a.match_score,
            "sent_at": a.sent_at.isoformat() if a.sent_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
        } for a in apps],
        "total": total, "page": page, "per_page": per_page,
    })


@router.post("/export", response_model=APIResponse)
async def export_data(
    profile_id: str = Query(..., description="Profile ID"),
    format: str = Query("json", pattern="^(csv|json)$"),
    svc: ExportService = Depends(get_export_service),
    _user_id: Optional[str] = Depends(get_current_user_id),
):
    """Export application data as CSV or JSON."""
    if format == "csv":
        data = await svc.export_csv(profile_id)
        return APIResponse(data={"format": "csv", "content": data, "filename": f"applications-{profile_id}.csv"})
    else:
        data = await svc.export_json(profile_id)
        return APIResponse(data={"format": "json", "content": data, "filename": f"applications-{profile_id}.json"})
