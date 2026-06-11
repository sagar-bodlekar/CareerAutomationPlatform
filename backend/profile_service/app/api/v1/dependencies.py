"""FastAPI dependency injection for services and DB sessions."""

from collections.abc import AsyncGenerator

from fastapi import Depends

from shared.database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.profile_service import ProfileService


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


async def get_profile_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProfileService:
    """Get ProfileService instance with DB session."""
    return ProfileService(session)
