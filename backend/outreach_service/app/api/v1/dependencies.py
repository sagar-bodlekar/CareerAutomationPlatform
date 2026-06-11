"""Outreach service dependencies."""

from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session

from ...services.cover_letter_service import CoverLetterService
from ...services.email_service import EmailService
from ...services.personalization_service import PersonalizationService
from ...services.template_service import TemplateService


async def get_cover_letter_service(db: AsyncSession = Depends(get_session)) -> CoverLetterService:
    return CoverLetterService(db)


async def get_email_service(db: AsyncSession = Depends(get_session)) -> EmailService:
    return EmailService(db)


async def get_personalization_service() -> PersonalizationService:
    return PersonalizationService()


async def get_template_service(db: AsyncSession = Depends(get_session)) -> TemplateService:
    return TemplateService(db)


async def get_current_user_id(request: Request) -> Optional[int]:
    return None
