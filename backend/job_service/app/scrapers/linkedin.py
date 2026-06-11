"""LinkedIn job scraper."""

import hashlib
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .base import JobScraper, ScrapeError


class LinkedInScraper(JobScraper):
    """Scrapes job listings from LinkedIn public job search."""

    SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @property
    def source_name(self) -> str:
        return "linkedin"

    async def fetch(self) -> list[dict]:
        """Fetch jobs from LinkedIn job search API."""
        headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENT),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.linkedin.com/jobs/",
        }
        params = {
            "keywords": self.config.get("query", "software engineer"),
            "location": self.config.get("location", ""),
            "f_TPR": self.config.get("time_range", ""),  # r86400 = past 24 hours
            "start": self.config.get("start", 0),
            "count": min(self.config.get("limit", 25), 25),  # LinkedIn max 25 per page
        }
        timeout = self.config.get("timeout", 30)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                response = await client.get(self.SEARCH_URL, headers=headers, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise ScrapeError(
                    f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                    self.source_name,
                    recoverable=(e.response.status_code != 429),
                )
            except httpx.TimeoutException:
                raise ScrapeError("Request timed out", self.source_name)
            except Exception as e:
                raise ScrapeError(f"Fetch failed: {e}", self.source_name)

            # Parse HTML response
            return self._parse_html(response.text)

    def _parse_html(self, html: str) -> list[dict]:
        """Parse LinkedIn search results HTML into raw job dicts."""
        soup = BeautifulSoup(html, "html.parser")
        raw_jobs = []

        job_cards = soup.find_all("li", class_=re.compile(r"jobs-search-results__list-item"))
        if not job_cards:
            # Try alternative selector
            job_cards = soup.find_all("div", class_=re.compile(r"job-search-card"))

        for card in job_cards:
            job = {}

            # Title
            title_el = card.find("a", class_=re.compile(r"job-card-list__title"))
            if title_el:
                job["title"] = title_el.get_text(strip=True)
                job["url"] = title_el.get("href", "")

            # Company
            company_el = card.find("span", class_=re.compile(r"job-card-container__company-name"))
            if company_el:
                job["company_name"] = company_el.get_text(strip=True)

            # Location
            location_el = card.find("span", class_=re.compile(r"job-card-container__metadata-item"))
            if location_el:
                job["location"] = location_el.get_text(strip=True)

            # Posted date
            date_el = card.find("time", class_=re.compile(r"job-card-container__listed-state"))
            if date_el:
                job["posted_date"] = date_el.get("datetime", "") or date_el.get_text(strip=True)

            # Entity URN for job ID
            urn = card.get("data-job-id", "") or card.get("id", "")
            if urn:
                job["id"] = urn

            if job.get("title") or job.get("company_name"):
                raw_jobs.append(job)

        return raw_jobs

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse LinkedIn job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            title = job.get("title", "")
            company = job.get("company_name", "")
            location = job.get("location", "")

            # Determine remote status from location
            is_remote = False
            location_type = None
            if location:
                loc_lower = location.lower()
                is_remote = "remote" in loc_lower
                location_type = "remote" if is_remote else "onsite"
                if "hybrid" in loc_lower:
                    location_type = "hybrid"

            external_id = job.get("id", "")
            external_id = f"linkedin_{external_id}" if external_id else None

            normalized = {
                "external_id": external_id,
                "title": title.strip() if title else "Unknown Position",
                "company_name": company.strip() if company else "Unknown Company",
                "company_description": None,
                "company_url": None,
                "company_logo": None,
                "location": location.strip() if location else None,
                "location_type": location_type,
                "is_remote": is_remote,
                "remote_type": location_type,
                "description": None,
                "requirements": None,
                "responsibilities": None,
                "required_skills": None,
                "nice_to_have_skills": None,
                "experience_min_years": None,
                "experience_max_years": None,
                "experience_level": None,
                "education_required": None,
                "degree_preferred": None,
                "salary_min": None,
                "salary_max": None,
                "salary_currency": None,
                "salary_period": None,
                "salary_visible": False,
                "employment_type": "full_time",
                "industry": None,
                "function": None,
                "department": None,
                "job_url": job.get("url", ""),
                "apply_url": job.get("url", ""),
                "posted_at": job.get("posted_date", None),
                "status": "active",
                "raw_data": job,
            }
            parsed.append(normalized)

        return parsed
