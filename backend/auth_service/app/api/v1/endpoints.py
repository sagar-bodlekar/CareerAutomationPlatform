"""Auth Service API endpoints.

All routes are under ``/api/v1/auth/`` and ``/api/v1/api-keys/``.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from shared.schemas.common import APIResponse

from app.middleware.jwt_middleware import get_current_user, verify_token
from app.models.models import AuthUser
from app.schemas import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    UserResponse,
)
from app.schemas.auth import TokenResponse
from app.services.api_key_service import ApiKeyService
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService
from app.api.v1.dependencies import (
    get_api_key_service,
    get_auth_service,
    get_oauth_service,
)

router = APIRouter(tags=["auth"])


# ─── Registration ────────────────────────────────────────────


@router.post("/auth/register", status_code=201, response_model=APIResponse)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user account.

    Returns the user info and a verification email will be sent.
    (Email sending is stubbed for now — wires in Phase 9.)
    """
    try:
        user = await auth_service.register(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return APIResponse(
        data=RegisterResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            is_verified=user.is_verified,
            created_at=user.created_at,
        ).model_dump(),
        message="Registration successful. Please verify your email.",
    )


# ─── Email Verification ──────────────────────────────────────


@router.post("/auth/verify-email", response_model=APIResponse)
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verify email address using a verification token."""
    success = await auth_service.verify_email(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    return APIResponse(message="Email verified successfully")


# ─── Login ───────────────────────────────────────────────────


@router.post("/auth/login", response_model=APIResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate with email and password. Returns JWT token pair."""
    user = await auth_service.authenticate(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    from app.core.tokens import token_manager

    tokens = await token_manager.create_token_pair(str(user.id))
    return APIResponse(data=tokens, message="Login successful")


# ─── Token Refresh ────────────────────────────────────────────


@router.post("/auth/refresh", response_model=APIResponse)
async def refresh_token(
    request: RefreshRequest,
):
    """Refresh an access token using a valid refresh token."""
    from app.core.tokens import token_manager

    tokens = await token_manager.refresh_access_token(request.refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return APIResponse(data=tokens, message="Token refreshed")


# ─── Logout ───────────────────────────────────────────────────


@router.post("/auth/logout", response_model=APIResponse)
async def logout(
    request: LogoutRequest,
    payload: dict = Depends(verify_token),
):
    """Logout by blacklisting the refresh token.

    Requires a valid access token in the Authorization header.
    The refresh token body should be the refresh token to invalidate.
    """
    from app.core.tokens import token_manager

    await token_manager.blacklist_token(request.refresh_token)
    return APIResponse(message="Logged out successfully")


# ─── Password Management ───────────────────────────────────────


@router.post("/auth/change-password", response_model=APIResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: AuthUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Change the current user's password."""
    success = await auth_service.change_password(current_user, request)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    return APIResponse(message="Password changed successfully")


@router.post("/auth/forgot-password", response_model=APIResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request a password reset email.

    Returns success regardless of whether the email exists (security best practice).
    """
    token = await auth_service.initiate_password_reset(request.email)
    # In Phase 9, this would send an email with the reset link
    # For now, return the token in dev mode for testing
    from app.core.config import settings

    result = {"message": "If the email exists, a reset link has been sent"}
    if settings.app_env == "development" and token:
        result["reset_token"] = token
    return APIResponse(data=result, message="Password reset initiated")


@router.post("/auth/reset-password", response_model=APIResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Reset password using a reset token received via email."""
    success = await auth_service.reset_password(request.token, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    return APIResponse(message="Password reset successfully")


# ─── Current User ─────────────────────────────────────────────


@router.get("/auth/me", response_model=APIResponse)
async def get_current_user_info(
    current_user: AuthUser = Depends(get_current_user),
):
    """Get the currently authenticated user's information."""
    return APIResponse(data=UserResponse.model_validate(current_user).model_dump())


# ─── OAuth ────────────────────────────────────────────────────


@router.get("/auth/oauth/{provider}")
async def oauth_initiate(provider: str):
    """Initiate OAuth2 flow for the given provider.

    Returns the authorization URL the client should redirect to.
    (Stub implementation — actual OAuth URLs differ per provider.)
    """
    if provider not in OAuthService.PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}. Supported: {', '.join(sorted(OAuthService.PROVIDERS))}",
        )

    # In production, generate the real OAuth authorize URL
    # For now, return a placeholder
    return APIResponse(
        data={
            "provider": provider,
            "authorization_url": f"/api/v1/auth/oauth/{provider}/authorize",
            "message": f"Redirect user to the OAuth provider's consent screen",
        }
    )


@router.get("/auth/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    oauth_service: OAuthService = Depends(get_oauth_service),
):
    """Handle OAuth2 callback from a provider.

    Exchanges the authorization code for tokens and creates/links
    the user account.
    (Stub implementation — wires real provider APIs in Phase 7.)
    """
    if provider not in OAuthService.PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )

    # Stub: In production, exchange `code` for tokens via the provider's API
    # For now, return a placeholder response
    return APIResponse(
        data={
            "provider": provider,
            "message": "OAuth callback received. Integration with provider API pending.",
        }
    )


@router.get("/auth/oauth/connections", response_model=APIResponse)
async def list_oauth_connections(
    current_user: AuthUser = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service),
):
    """List all OAuth connections for the current user."""
    connections = await oauth_service.get_user_connections(current_user.id)
    return APIResponse(
        data=[
            {
                "provider": c.provider,
                "connected_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in connections
        ]
    )


@router.delete("/auth/oauth/{provider}", response_model=APIResponse)
async def disconnect_oauth(
    provider: str,
    current_user: AuthUser = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service),
):
    """Disconnect an OAuth provider from the current user's account."""
    if provider not in OAuthService.PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )

    success = await oauth_service.disconnect_provider(current_user.id, provider)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No connection found for this provider",
        )
    return APIResponse(message=f"{provider} account disconnected")


# ─── API Key Management ────────────────────────────────────────


@router.post("/api-keys", status_code=201, response_model=APIResponse)
async def create_api_key(
    request: ApiKeyCreateRequest,
    current_user: AuthUser = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    """Create a new API key for service-to-service auth.

    The full key is only shown once in the response.
    """
    api_key, full_key = await api_key_service.create_key(
        user=current_user,
        name=request.name,
        scopes=request.scopes,
        expires_at=request.expires_at,
    )
    return APIResponse(
        data=ApiKeyCreateResponse(
            id=api_key.id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            key=full_key,
            scopes=api_key.scopes,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
        ).model_dump(),
        message="API key created. Save the key now — it won't be shown again.",
    )


@router.get("/api-keys", response_model=APIResponse)
async def list_api_keys(
    current_user: AuthUser = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    """List all API keys for the current user."""
    keys = await api_key_service.list_keys(current_user.id)
    return APIResponse(
        data=[ApiKeyResponse.model_validate(k).model_dump() for k in keys]
    )


@router.delete("/api-keys/{key_id}", response_model=APIResponse)
async def revoke_api_key(
    key_id: uuid.UUID,
    current_user: AuthUser = Depends(get_current_user),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
):
    """Revoke an API key (soft delete)."""
    success = await api_key_service.revoke_key(key_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return APIResponse(message="API key revoked")
