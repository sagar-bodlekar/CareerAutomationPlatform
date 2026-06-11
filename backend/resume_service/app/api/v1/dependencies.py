"""FastAPI dependency injection for Resume Service."""

from collections.abc import AsyncGenerator

from fastapi import Depends

from shared.database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.resume_service import ResumeService
from app.services.template_service import TemplateService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with automatic commit/rollback."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_resume_service(
    session: AsyncSession = Depends(get_db_session),
) -> ResumeService:
    """Get ResumeService instance."""
    return ResumeService(session)


async def get_template_service(
    session: AsyncSession = Depends(get_db_session),
) -> TemplateService:
    """Get TemplateService instance."""
    return TemplateService(session)
