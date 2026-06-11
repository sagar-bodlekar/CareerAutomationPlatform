"""FastAPI dependency injection for auth services."""

from collections.abc import AsyncGenerator

from fastapi import Depends

from shared.database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.api_key_service import ApiKeyService
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService


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


async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    """Get AuthService instance."""
    return AuthService(session)


async def get_oauth_service(
    session: AsyncSession = Depends(get_db_session),
) -> OAuthService:
    """Get OAuthService instance."""
    return OAuthService(session)


async def get_api_key_service(
    session: AsyncSession = Depends(get_db_session),
) -> ApiKeyService:
    """Get ApiKeyService instance."""
    return ApiKeyService(session)
