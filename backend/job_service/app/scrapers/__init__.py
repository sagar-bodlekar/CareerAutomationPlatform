from .base import JobScraper, ScrapeResult, ScrapeError
from .remoteok import RemoteOKScraper
from .naukri import NaukriScraper
from .wellfound import WellfoundScraper
from .linkedin import LinkedInScraper
from .generic import GenericCareerPageScraper

__all__ = [
    "JobScraper",
    "ScrapeResult",
    "ScrapeError",
    "RemoteOKScraper",
    "NaukriScraper",
    "WellfoundScraper",
    "LinkedInScraper",
    "GenericCareerPageScraper",
]

SCRAPER_REGISTRY: dict[str, type[JobScraper]] = {
    "remoteok": RemoteOKScraper,
    "naukri": NaukriScraper,
    "wellfound": WellfoundScraper,
    "linkedin": LinkedInScraper,
    "generic": GenericCareerPageScraper,
}
