"""Shared application configuration loaded from environment variables."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Base configuration for all microservices."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────
    app_name: str = "AI Career Automation Platform"
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "INFO"

    # ─── Database ────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/career_platform"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "career_platform"

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ─── Redis ───────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # ─── Celery ──────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # ─── MinIO ───────────────────────────────────────────────
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_use_ssl: bool = False
    minio_resumes_bucket: str = "resumes"
    minio_cover_letters_bucket: str = "cover-letters"
    minio_avatars_bucket: str = "avatars"
    minio_scraping_bucket: str = "scraping-artifacts"

    # ─── Auth / JWT ──────────────────────────────────────────
    jwt_secret: str = "change-this-to-a-random-256-bit-secret-in-production"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ─── AI / LLM ────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "llama3.2:8b"
    localai_base_url: str = "http://localhost:8080"
    localai_default_model: str = "llama-3.2-8b-instruct"

    # ─── Email ───────────────────────────────────────────────
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@career-platform.local"
    smtp_from_name: str = "Career Platform"

    # ─── API Gateway ─────────────────────────────────────────
    api_rate_limit_per_minute: int = 100
    api_burst_limit: int = 20
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


# Global singleton
settings = AppConfig()
