"""Service-specific configuration for Resume Service."""

from shared.config import AppConfig


class ServiceConfig(AppConfig):
    """Resume Service configuration."""

    service_name: str = "resume_service"
    service_port: int = 8003

    # MinIO resume bucket (overrides default)
    minio_resumes_bucket: str = "resumes"


settings = ServiceConfig()
