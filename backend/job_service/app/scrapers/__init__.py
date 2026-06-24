from .base import JobScraper, ScrapeResult, ScrapeError
from .remoteok import RemoteOKScraper
from .naukri import NaukriScraper  # Legacy BeautifulSoup version (fallback)
from .naukri_playwright import NaukriPlaywrightScraper  # Primary Playwright version
from .wellfound import WellfoundScraper
from .linkedin import LinkedInScraper
from .generic import GenericCareerPageScraper

__all__ = [
    "JobScraper",
    "ScrapeResult",
    "ScrapeError",
    "RemoteOKScraper",
    "NaukriScraper",
    "NaukriPlaywrightScraper",
    "WellfoundScraper",
    "LinkedInScraper",
    "GenericCareerPageScraper",
]

SCRAPER_REGISTRY: dict[str, type[JobScraper]] = {
    "remoteok": RemoteOKScraper,
    # Naukri uses Playwright (headless browser) because the site is a JS-rendered SPA
    "naukri": NaukriPlaywrightScraper,
    "naukri-legacy": NaukriScraper,  # Legacy BeautifulSoup version (may not work)
    "naukri-playwright": NaukriPlaywrightScraper,
    "wellfound": WellfoundScraper,
    "linkedin": LinkedInScraper,
    "generic": GenericCareerPageScraper,
}
