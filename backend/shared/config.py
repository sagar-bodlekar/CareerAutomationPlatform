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

    # ─── AI / LLM (Google Gemini — Primary) ────────────────────
    gemini_api_key: Optional[str] = None
    gemini_default_model: str = "gemini-2.0-flash"
    gemini_pro_model: str = "gemini-1.5-pro"

    @property
    def gemini_api_key_required(self) -> str:
        """Get Gemini API key or raise clear error."""
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required for AI features. "
                "Get your free API key at: https://aistudio.google.com/"
            )
        return self.gemini_api_key

    # ─── AI / LLM (Groq — Secondary / Fallback) ────────────────
    groq_api_key: Optional[str] = None
    groq_default_model: str = "llama-3.3-70b-versatile"
    groq_fallback_model: str = "mixtral-8x7b-32768"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    @property
    def groq_api_key_required(self) -> str:
        """Get Groq API key or raise clear error."""
        if not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required for Groq fallback. "
                "Get your free API key at: https://console.groq.com/"
            )
        return self.groq_api_key

    @property
    def llm_fallback_chain(self) -> list[tuple[str, str]]:
        """Fallback chain: Gemini primary → Groq secondary."""
        chain = []
        if self.gemini_api_key:
            chain.append(("gemini", self.gemini_default_model))
            chain.append(("gemini", self.gemini_pro_model))
        if self.groq_api_key:
            chain.append(("groq", self.groq_default_model))
            chain.append(("groq", self.groq_fallback_model))
        return chain

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
