"""Service-specific configuration for Auth Service."""

from pydantic import Field

from shared.config import AppConfig


class AuthServiceConfig(AppConfig):
    """Auth Service configuration."""

    service_name: str = "auth_service"
    service_port: int = 8002

    # JWT
    jwt_algorithm: str = Field(default="HS256")


settings = AuthServiceConfig()
