"""Application service dependencies."""

from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session

from ...services.application_service import ApplicationService


async def get_application_service(db: AsyncSession = Depends(get_session)) -> ApplicationService:
    return ApplicationService(db)


async def get_current_user_id(request: Request) -> Optional[int]:
    return None
