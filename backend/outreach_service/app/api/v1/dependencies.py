"""FastAPI dependency injection for services and DB sessions."""

from collections.abc import AsyncGenerator

from fastapi import Depends

from shared.database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.service import ExampleService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_service(
    session: AsyncSession = Depends(get_db_session),
) -> ExampleService:
    """Get example service instance."""
    return ExampleService(session)
