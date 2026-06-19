"""Resume Service API endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from shared.schemas.common import APIResponse

from app.core.config import settings
from app.middleware.auth_middleware import verify_token
from app.models.models import Resume
from app.schemas import (
    ATSOptimizeResponse,
    ResumeCreate,
    ResumeGenerationRequest,
    ResumeOptimizeRequest,
    ResumeResponse,
    ResumeSummary,
    ResumeTemplateCreate,
    ResumeTemplateResponse,
    ResumeTemplateUpdate,
    ResumeUpdate,
)
from app.services.ats.optimizer import ATSOptimizer
from app.services.content_assembler import ContentAssembler
from app.services.pdf_generator import PDFGenerator
from app.services.resume_service import ResumeService
from app.services.template_service import TemplateService
from app.api.v1.dependencies import (
    get_resume_service,
    get_template_service,
)

router = APIRouter(tags=["resumes"])


# ─── Resume CRUD ─────────────────────────────────────────────


@router.post("/resumes", status_code=201, response_model=APIResponse)
async def create_resume(
    data: ResumeCreate,
    service: ResumeService = Depends(get_resume_service),
    payload: dict = Depends(verify_token),
):
    """Create a master resume from profile data."""
    user_id = uuid.UUID(payload["sub"])
    resume = await service.create_resume(user_id, data)
    return APIResponse(
        data=ResumeResponse.model_validate(resume).model_dump(),
        message="Resume created",
    )


@router.get("/resumes/{resume_id}", response_model=APIResponse)
async def get_resume(
    resume_id: uuid.UUID,
    service: ResumeService = Depends(get_resume_service),
    payload: dict = Depends(verify_token),
):
    """Get resume by ID with file metadata."""
    resume = await service.get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return APIResponse(
        data=ResumeResponse.model_validate(resume).model_dump()
    )


@router.put("/resumes/{resume_id}", response_model=APIResponse)
async def update_resume(
    resume_id: uuid.UUID,
    data: ResumeUpdate,
    service: ResumeService = Depends(get_resume_service),
    payload: dict = Depends(verify_token),
):
    """Update resume metadata or content."""
    user_id = uuid.UUID(payload["sub"])
    resume = await service.update_resume(resume_id, data, user_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return APIResponse(
        data=ResumeResponse.model_validate(resume).model_dump(),
        message="Resume updated",
    )


@router.delete("/resumes/{resume_id}", response_model=APIResponse)
async def delete_resume(
    resume_id: uuid.UUID,
    service: ResumeService = Depends(get_resume_service),
    payload: dict = Depends(verify_token),
):
    """Soft delete a resume."""
    user_id = uuid.UUID(payload["sub"])
    deleted = await service.soft_delete_resume(resume_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found")
    return APIResponse(message="Resume deleted")


@router.get("/resumes", response_model=APIResponse)
async def list_resumes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_deleted: bool = False,
    service: ResumeService = Depends(get_resume_service),
    payload: dict = Depends(verify_token),
):
    """List resumes for the authenticated user."""
    user_id = uuid.UUID(payload["sub"])
    resumes, total = await service.list_resumes(
        user_id=user_id,
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
    )
    summaries = [service.to_summary(r) for r in resumes]

    return APIResponse(
        data={
            "items": [s.model_dump() for s in summaries],
            "total": total,
            "page": page,
            "per_page": page_size,
        },
    )


# ─── Generate PDF ────────────────────────────────────────────


@router.post("/resumes/{resume_id}/generate", response_model=APIResponse)
async def generate_resume_pdf(
    resume_id: uuid.UUID,
    request: ResumeGenerationRequest,
    service: ResumeService = Depends(get_resume_service),
    template_service: TemplateService = Depends(get_template_service),
    payload: dict = Depends(verify_token),
):
    """Generate a role-specific resume PDF and store in MinIO."""
    resume = await service.get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Determine template
    template_name = "master"
    if request.template_id:
        tmpl = await template_service.get_template(request.template_id)
        if tmpl:
            template_name = tmpl.name

    # Get profile data (stub — in production, call Profile Service)
    # For now, use the resume's stored content or empty
    profile_data = {
        "personal_info": resume.content.get("personal_info", {}),
        "headline": resume.target_role or resume.title,
        "summary": resume.content.get("summary", ""),
        "skills": resume.content.get("skills", []),
        "work_experiences": resume.content.get("work_experiences", []),
        "education": resume.content.get("education", []),
        "projects": resume.content.get("projects", []),
        "certifications": resume.content.get("certifications", []),
        "social_links": resume.content.get("social_links", []),
    }

    # Update target role
    if request.target_role:
        resume.target_role = request.target_role
    if request.target_job_id:
        resume.target_job_id = request.target_job_id

    from app.services.pdf_generator import PDFGenerator

    pdf_gen = PDFGenerator()
    resume_file = await pdf_gen.generate_and_store_pdf(
        resume=resume,
        profile_data=profile_data,
        session=service.session,
        template_name=template_name,
    )

    return APIResponse(
        data={
            "resume_id": str(resume.id),
            "file_id": str(resume_file.id),
            "filename": resume_file.filename,
            "size_bytes": resume_file.file_size_bytes,
            "download_url": resume_file.minio_presigned_url,
            "template": template_name,
        },
        message="PDF generated successfully",
    )


@router.get("/resumes/{resume_id}/download", response_model=APIResponse)
async def download_resume_pdf(
    resume_id: uuid.UUID,
    file_id: uuid.UUID | None = None,
    service: ResumeService = Depends(get_resume_service),
    payload: dict = Depends(verify_token),
):
    """Get a presigned download URL for a resume PDF.

    If ``file_id`` is omitted, returns the latest file.
    """
    resume = await service.get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    if file_id:
        url = await service.generate_presigned_url(file_id)
    else:
        # Latest file
        if not resume.files:
            raise HTTPException(status_code=404, detail="No generated files")
        latest = resume.files[-1]
        url = await service.generate_presigned_url(latest.id)

    if url is None:
        raise HTTPException(status_code=404, detail="File not found")

    return APIResponse(
        data={"download_url": url, "expires_in_hours": 1}
    )


# ─── ATS Optimization ────────────────────────────────────────


@router.post("/resumes/{resume_id}/optimize", response_model=APIResponse)
async def optimize_resume_ats(
    resume_id: uuid.UUID,
    request: ResumeOptimizeRequest,
    service: ResumeService = Depends(get_resume_service),
    payload: dict = Depends(verify_token),
):
    """Run ATS optimization on a resume against a job description.

    Returns score breakdown, keyword analysis, and recommendations.
    """
    resume = await service.get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    from app.services.content_assembler import ContentAssembler

    assembler = ContentAssembler()
    resume_content = assembler.from_profile({
        "personal_info": resume.content.get("personal_info", {}),
        "headline": resume.target_role or "",
        "summary": resume.content.get("summary", ""),
        "skills": resume.content.get("skills", []),
        "work_experiences": resume.content.get("work_experiences", []),
        "education": resume.content.get("education", []),
        "projects": resume.content.get("projects", []),
        "certifications": resume.content.get("certifications", []),
    })

    optimizer = ATSOptimizer()
    result = await optimizer.analyze_and_optimize(
        resume_content=resume_content,
        job_description=request.job_description,
    )

    # Store score on resume
    resume.ats_score = result["score"]
    resume.ats_score_breakdown = result["score_breakdown"]
    await service.session.flush()

    return APIResponse(
        data={
            "resume_id": str(resume.id),
            "ats_score": result["score"],
            "score_breakdown": result["score_breakdown"],
            "recommendations": result["recommendations"],
            "missing_keywords": result["missing_keywords"][:20],
            "matched_keywords": result["matched_keywords"][:20],
        },
        message="ATS analysis complete",
    )


# ─── Templates ────────────────────────────────────────────────


@router.get("/templates", response_model=APIResponse)
async def list_templates(
    template_service: TemplateService = Depends(get_template_service),
):
    """List all active resume templates."""
    templates = await template_service.list_templates(active_only=True)
    return APIResponse(
        data=[ResumeTemplateResponse.model_validate(t).model_dump() for t in templates]
    )


@router.get("/templates/{template_id}", response_model=APIResponse)
async def get_template(
    template_id: uuid.UUID,
    template_service: TemplateService = Depends(get_template_service),
):
    """Get a specific resume template."""
    template = await template_service.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return APIResponse(
        data=ResumeTemplateResponse.model_validate(template).model_dump()
    )


@router.post("/templates", status_code=201, response_model=APIResponse)
async def create_template(
    data: ResumeTemplateCreate,
    template_service: TemplateService = Depends(get_template_service),
):
    """Create a new resume template (admin)."""
    template = await template_service.create_template(data)
    return APIResponse(
        data=ResumeTemplateResponse.model_validate(template).model_dump(),
        message="Template created",
    )


@router.put("/templates/{template_id}", response_model=APIResponse)
async def update_template(
    template_id: uuid.UUID,
    data: ResumeTemplateUpdate,
    template_service: TemplateService = Depends(get_template_service),
):
    """Update a resume template."""
    template = await template_service.update_template(template_id, data)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return APIResponse(
        data=ResumeTemplateResponse.model_validate(template).model_dump(),
        message="Template updated",
    )


@router.delete("/templates/{template_id}", response_model=APIResponse)
async def delete_template(
    template_id: uuid.UUID,
    template_service: TemplateService = Depends(get_template_service),
):
    """Delete a resume template."""
    deleted = await template_service.delete_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    return APIResponse(message="Template deleted")


# ─── Seed Templates ──────────────────────────────────────────


@router.post("/templates/seed", response_model=APIResponse)
async def seed_default_templates(
    template_service: TemplateService = Depends(get_template_service),
):
    """Seed default resume templates from file system."""
    templates = await template_service.seed_default_templates()
    return APIResponse(
        data=[ResumeTemplateResponse.model_validate(t).model_dump() for t in templates],
        message=f"{len(templates)} templates seeded",
    )
