"""Base scraper interface and shared types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


class ScrapeError(Exception):
    """Raised when a scraper encounters a non-recoverable error."""

    def __init__(self, message: str, source: str, recoverable: bool = True):
        self.message = message
        self.source = source
        self.recoverable = recoverable
        super().__init__(f"[{source}] {message}")


@dataclass
class ScrapeResult:
    """Normalized result from a single scrape operation."""

    source_name: str
    jobs: list[dict] = field(default_factory=list)
    total_found: int = 0
    total_new: int = 0
    total_duplicates: int = 0
    total_errors: int = 0
    errors: list[str] = field(default_factory=list)
    success: bool = True


class JobScraper(ABC):
    """Abstract base class for job scrapers.

    Subclasses must implement:
    - source_name: human-readable name
    - fetch(): retrieve raw data from source
    - parse(): convert raw data to normalized Job dicts
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._session = None

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable source name (e.g., 'RemoteOK')."""
        ...

    @abstractmethod
    async def fetch(self) -> list[dict]:
        """Retrieve raw job listings from the source.

        Returns:
            List of raw job data dicts (source-specific format).

        Raises:
            ScrapeError: if the source is unreachable or returns an error.
        """
        ...

    @abstractmethod
    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Convert raw job data to normalized Job schema dicts.

        Args:
            raw_jobs: Raw job data from fetch().

        Returns:
            List of dicts matching the JobCreate schema.
        """
        ...

    async def scrape(self) -> ScrapeResult:
        """Run the full scrape pipeline: fetch -> parse -> return results.

        Returns:
            ScrapeResult with parsed jobs and metadata.
        """
        result = ScrapeResult(source_name=self.source_name)
        try:
            raw_data = await self.fetch()
            result.total_found = len(raw_data)
            parsed = self.parse(raw_data)
            result.jobs = parsed
        except ScrapeError as e:
            result.success = False
            result.errors.append(str(e))
            result.total_errors = 1
        except Exception as e:
            result.success = False
            result.errors.append(f"Unexpected error: {e}")
            result.total_errors = 1
        return result

    async def close(self) -> None:
        """Clean up any resources (HTTP sessions, etc.)."""
        if self._session:
            await self._session.close()
