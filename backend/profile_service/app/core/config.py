"""Service-specific configuration for Profile Service."""

from shared.config import AppConfig


class ServiceConfig(AppConfig):
    """Profile Service configuration."""

    service_name: str = "profile_service"
    service_port: int = 8001


settings = ServiceConfig()
