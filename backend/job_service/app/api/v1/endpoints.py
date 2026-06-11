"""Job service API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from shared.schemas.common import APIResponse
from shared.schemas.pagination import PaginatedResponse, PaginationMeta

from ...schemas.filters import JobFilterParams
from ...schemas.job import JobCreate, JobResponse, JobUpdate
from ...schemas.source import JobSourceCreate, JobSourceResponse, JobSourceUpdate
from ...services.dedup_service import DeduplicationService
from ...services.job_service import JobService
from ...services.scraper_service import ScraperService
from .dependencies import (
    get_current_user_id,
    get_dedup_service,
    get_job_service,
    get_scraper_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ─── Job endpoints ───────────────────────────────────────


@router.get("", response_model=PaginatedResponse[JobResponse])
async def list_jobs(
    query: Optional[str] = Query(None, description="Full-text search query"),
    title: Optional[str] = Query(None),
    company_name: Optional[str] = Query(None),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    location: Optional[str] = Query(None),
    location_type: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    experience_min: Optional[int] = Query(None, ge=0),
    experience_max: Optional[int] = Query(None, ge=0),
    experience_level: Optional[str] = Query(None),
    salary_min: Optional[float] = Query(None, ge=0),
    salary_max: Optional[float] = Query(None, ge=0),
    employment_type: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    sort_by: str = Query("posted_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """List and search jobs with filters and pagination."""
    filters = JobFilterParams(
        query=query,
        title=title,
        company_name=company_name,
        skills=skills,
        location=location,
        location_type=location_type,
        is_remote=is_remote,
        experience_min=experience_min,
        experience_max=experience_max,
        experience_level=experience_level,
        salary_min=salary_min,
        salary_max=salary_max,
        employment_type=employment_type,
        industry=industry,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )

    jobs, total = await job_service.list_jobs(filters)
    return PaginatedResponse(
        data=[JobResponse.model_validate(j) for j in jobs],
        meta=PaginationMeta.compute(
            page=page,
            per_page=per_page,
            total=total,
        ),
    )


@router.get("/{job_id}", response_model=APIResponse[JobResponse])
async def get_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get job details by ID."""
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return APIResponse(data=JobResponse.model_validate(job))


@router.post("", response_model=APIResponse[JobResponse], status_code=201)
async def create_job(
    data: JobCreate,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Create a new job listing."""
    job = await job_service.create_job(data)
    return APIResponse(data=JobResponse.model_validate(job))


@router.put("/{job_id}", response_model=APIResponse[JobResponse])
async def update_job(
    job_id: int,
    data: JobUpdate,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Update an existing job listing."""
    job = await job_service.update_job(job_id, data)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return APIResponse(data=JobResponse.model_validate(job))


@router.delete("/{job_id}", response_model=APIResponse)
async def delete_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Soft-delete a job listing."""
    success = await job_service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return APIResponse(data={"message": "Job deleted successfully"})


# ─── Scraping endpoints ──────────────────────────────────


@router.post("/refresh", response_model=APIResponse)
async def refresh_jobs(
    source: Optional[str] = Query(None, description="Specific source to scrape"),
    scraper_service: ScraperService = Depends(get_scraper_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Trigger immediate job scraping from one or all sources."""
    if source:
        try:
            result = await scraper_service.scrape_source(source, save=True)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return APIResponse(data={
            "source": source,
            "found": result.total_found,
            "new": result.total_new,
            "duplicates": result.total_duplicates,
            "errors": result.total_errors,
            "success": result.success,
        })

    results = await scraper_service.scrape_all_active()
    summary = {}
    total_new = 0
    total_errors = 0
    for name, result in results.items():
        summary[name] = {
            "found": result.total_found,
            "new": result.total_new,
            "duplicates": result.total_duplicates,
            "errors": result.total_errors,
            "success": result.success,
        }
        total_new += result.total_new
        total_errors += result.total_errors

    return APIResponse(data={
        "sources": summary,
        "total_new": total_new,
        "total_errors": total_errors,
    })


# ─── Source endpoints ────────────────────────────────────


@router.get("/sources", response_model=APIResponse[list[JobSourceResponse]])
async def list_sources(
    active_only: bool = Query(True),
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """List configured job sources."""
    sources = await job_service.list_sources(active_only=active_only)
    return APIResponse(data=[JobSourceResponse.model_validate(s) for s in sources])


@router.post("/sources", response_model=APIResponse[JobSourceResponse], status_code=201)
async def create_source(
    data: JobSourceCreate,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Create a new job source configuration."""
    source = await job_service.create_source(data)
    return APIResponse(data=JobSourceResponse.model_validate(source))


@router.get("/sources/{source_id}", response_model=APIResponse[JobSourceResponse])
async def get_source(
    source_id: int,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get a job source by ID."""
    source = await job_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return APIResponse(data=JobSourceResponse.model_validate(source))


@router.put("/sources/{source_id}", response_model=APIResponse[JobSourceResponse])
async def update_source(
    source_id: int,
    data: JobSourceUpdate,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Update a job source configuration."""
    source = await job_service.update_source(source_id, data)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return APIResponse(data=JobSourceResponse.model_validate(source))


@router.delete("/sources/{source_id}", response_model=APIResponse)
async def delete_source(
    source_id: int,
    job_service: JobService = Depends(get_job_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Delete a job source."""
    success = await job_service.delete_source(source_id)
    if not success:
        raise HTTPException(status_code=404, detail="Source not found")
    return APIResponse(data={"message": "Source deleted successfully"})


@router.post("/sources/{source_id}/test", response_model=APIResponse)
async def test_source(
    source_id: int,
    job_service: JobService = Depends(get_job_service),
    scraper_service: ScraperService = Depends(get_scraper_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Test scraper connection for a source."""
    source = await job_service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    config = source.config or {}
    config.update({
        "name": source.name,
        "base_url": source.base_url,
        "limit": 3,  # Small sample for testing
    })

    try:
        result = await scraper_service.scrape_source(source.name, config=config, save=False)
        return APIResponse(data={
            "source": source.name,
            "success": result.success,
            "jobs_found": result.total_found,
            "errors": result.errors,
            "sample_jobs": result.jobs[:3] if result.jobs else [],
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
