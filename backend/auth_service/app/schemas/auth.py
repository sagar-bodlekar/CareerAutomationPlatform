"""Auth schemas — register, login, token, password management."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ─── Registration ─────────────────────────────────────────────


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=200)


class RegisterResponse(BaseModel):
    """Response body after successful registration."""

    id: UUID
    email: str
    display_name: str | None = None
    is_verified: bool = False
    created_at: datetime


# ─── Login ────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response body with JWT token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""

    sub: str
    exp: int
    type: str


# ─── Token Refresh ────────────────────────────────────────────


class RefreshRequest(BaseModel):
    """Request body to refresh an access token."""

    refresh_token: str


# ─── Logout ────────────────────────────────────────────────────


class LogoutRequest(BaseModel):
    """Request body to invalidate a refresh token."""

    refresh_token: str


# ─── Password Management ───────────────────────────────────────


class ChangePasswordRequest(BaseModel):
    """Request body to change the current user's password."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    """Request body to initiate password reset."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body to complete password reset."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ─── User Info ─────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user information response."""

    id: UUID
    email: str
    display_name: str | None = None
    is_verified: bool = False
    is_active: bool = True
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
