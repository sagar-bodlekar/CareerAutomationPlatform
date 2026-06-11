"""Service-specific configuration.

Extends the shared AppConfig with service-specific settings.
"""

from shared.config import AppConfig


class ServiceConfig(AppConfig):
    """Service-specific configuration."""

    service_name: str = "application_service"
    service_port: int = 8000


settings = ServiceConfig()
