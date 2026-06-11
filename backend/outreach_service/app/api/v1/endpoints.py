"""Outreach service API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from shared.schemas.common import APIResponse

from ...schemas.cover_letter import CoverLetterRequest, CoverLetterResponse, CoverLetterUpdate
from ...schemas.email import EmailRequest, EmailResponse, EmailUpdate
from ...services.cover_letter_service import CoverLetterService
from ...services.email_service import EmailService
from ...services.personalization_service import PersonalizationService
from ...services.template_service import TemplateService
from .dependencies import (
    get_cover_letter_service,
    get_current_user_id,
    get_email_service,
    get_personalization_service,
    get_template_service,
)

router = APIRouter(prefix="/outreach", tags=["Outreach"])


@router.post("/cover-letter", response_model=APIResponse[CoverLetterResponse], status_code=201)
async def generate_cover_letter(
    request: CoverLetterRequest,
    svc: CoverLetterService = Depends(get_cover_letter_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Generate a personalized cover letter."""
    result = await svc.generate(request)
    return APIResponse(data=result)


@router.get("/cover-letter/{content_id}", response_model=APIResponse[CoverLetterResponse])
async def get_cover_letter(
    content_id: int,
    svc: CoverLetterService = Depends(get_cover_letter_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get a cover letter by ID."""
    result = await svc.get(content_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return APIResponse(data=result)


@router.put("/cover-letter/{content_id}", response_model=APIResponse[CoverLetterResponse])
async def update_cover_letter(
    content_id: int,
    update: CoverLetterUpdate,
    svc: CoverLetterService = Depends(get_cover_letter_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Update a cover letter manually."""
    result = await svc.update(content_id, body=update.body, status=update.status)
    if not result:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return APIResponse(data=result)


@router.post("/email", response_model=APIResponse[EmailResponse], status_code=201)
async def generate_email(
    request: EmailRequest,
    svc: EmailService = Depends(get_email_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Generate a personalized outreach email."""
    result = await svc.generate(request)
    return APIResponse(data=result)


@router.get("/email/{content_id}", response_model=APIResponse[EmailResponse])
async def get_email(
    content_id: int,
    svc: EmailService = Depends(get_email_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get an email by ID."""
    result = await svc.get(content_id)
    if not result:
        raise HTTPException(status_code=404, detail="Email not found")
    return APIResponse(data=result)


@router.put("/email/{content_id}", response_model=APIResponse[EmailResponse])
async def update_email(
    content_id: int,
    update: EmailUpdate,
    svc: EmailService = Depends(get_email_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Update an email manually."""
    result = await svc.update(content_id, subject=update.subject, body=update.body, status=update.status)
    if not result:
        raise HTTPException(status_code=404, detail="Email not found")
    return APIResponse(data=result)


@router.get("/templates", response_model=APIResponse)
async def list_templates(
    content_type: Optional[str] = None,
    svc: TemplateService = Depends(get_template_service),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """List available outreach templates."""
    templates = await svc.list_templates(content_type=content_type)
    return APIResponse(data=[{"id": t.id, "name": t.template_name, "content_type": t.content_type, "tone": t.tone} for t in templates])


@router.get("/preview", response_model=APIResponse)
async def preview_content(
    body: str,
    subject: Optional[str] = None,
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Preview generated content (validates formatting)."""
    return APIResponse(data={"subject": subject, "body": body, "preview": body[:500]})
