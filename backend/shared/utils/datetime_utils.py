"""Datetime utility functions for consistent timestamp handling."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime | None, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str | None:
    """Format a datetime to string. Returns None if input is None."""
    if dt is None:
        return None
    return dt.strftime(fmt)


def parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO 8601 datetime string. Returns None if input is None or invalid."""
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def years_between(start: datetime, end: datetime | None = None) -> float:
    """Calculate decimal years between two datetimes."""
    end = end or utc_now()
    days = (end - start).days
    return round(days / 365.25, 1)
