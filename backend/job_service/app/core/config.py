"""Job service configuration."""

from shared.config import AppConfig

settings = AppConfig()

JOB_SERVICE_SETTINGS = {
    "app_name": "Job Service",
    "app_version": "0.1.0",
    "scrape_timeout_seconds": 30,
    "scrape_retry_count": 3,
    "scrape_retry_delay_seconds": 5,
    "dedup_redis_ttl_hours": 48,
    "max_jobs_per_scrape": 500,
    "default_scrape_interval_minutes": 60,
}
