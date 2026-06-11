"""JWT authentication middleware and FastAPI dependency.

Provides:
- ``verify_token`` dependency for protecting individual routes.
- ``get_current_user`` dependency that resolves the user from the token.
"""

from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import async_session_factory

from app.core.security import decode_token
from app.core.tokens import token_manager
from app.models.models import AuthUser

# FastAPI security scheme (auto-extracts Bearer token from Authorization header)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for middleware use."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Verify a JWT access token and return its payload.

    Raises 401 if the token is missing, invalid, expired, or blacklisted.

    Returns:
        Decoded token payload dict.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Check blacklist
    if await token_manager.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    # Decode and validate
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Ensure it's an access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Use an access token.",
        )

    return payload


async def get_current_user(
    payload: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_db_session),
) -> AuthUser:
    """Resolve the current authenticated user from the JWT token.

    Returns:
        The ``AuthUser`` instance.

    Raises 401 if the user is not found or is inactive.
    """
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await session.execute(
        select(AuthUser).where(AuthUser.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> AuthUser | None:
    """Resolve the current user if a valid token is provided, else ``None``.

    Useful for endpoints that behave differently for authenticated users
    but are also accessible anonymously.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    if await token_manager.is_blacklisted(token):
        return None

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    result = await session.execute(
        select(AuthUser).where(AuthUser.id == UUID(user_id))
    )
    return result.scalar_one_or_none()
