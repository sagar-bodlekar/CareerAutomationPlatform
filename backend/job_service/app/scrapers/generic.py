"""Generic career page scraper for configurable company career pages."""

import hashlib
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .base import JobScraper, ScrapeError


class GenericCareerPageScraper(JobScraper):
    """Scrapes job listings from any company's career page.

    Configure via config dict with CSS selectors:
    - job_listing_selector: CSS selector for job listing container
    - title_selector: CSS selector for job title within listing
    - url_selector: CSS selector for job URL/link
    - location_selector: CSS selector for location
    - description_selector: CSS selector for description (optional)
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @property
    def source_name(self) -> str:
        return self.config.get("name", "generic")

    async def fetch(self) -> list[dict]:
        """Fetch jobs from configured career page URL."""
        url = self.config.get("career_page_url", "")
        if not url:
            raise ScrapeError("No career_page_url configured", self.source_name)

        headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENT),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        timeout = self.config.get("timeout", 30)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise ScrapeError(
                    f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                    self.source_name,
                )
            except httpx.TimeoutException:
                raise ScrapeError("Request timed out", self.source_name)
            except Exception as e:
                raise ScrapeError(f"Fetch failed: {e}", self.source_name)

            # Try JSON API first, then HTML parsing
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                return self._parse_json_api(response.json())
            else:
                return self._parse_html(response.text, url)

    def _parse_json_api(self, data: dict | list) -> list[dict]:
        """Parse response from JSON-based career page API."""
        raw_jobs = []
        jobs_data = data

        # Handle common API response structures
        if isinstance(data, dict):
            for key in ["jobs", "data", "results", "items", "positions", "listings"]:
                if key in data and isinstance(data[key], list):
                    jobs_data = data[key]
                    break

        if isinstance(jobs_data, list):
            for job in jobs_data:
                if isinstance(job, dict) and job.get("title"):
                    raw_jobs.append(job)

        return raw_jobs

    def _parse_html(self, html: str, base_url: str) -> list[dict]:
        """Parse HTML career page using configured CSS selectors."""
        soup = BeautifulSoup(html, "html.parser")
        raw_jobs = []

        job_listing_selector = self.config.get("job_listing_selector", "li, .job-listing, .posting, .job, tr")
        title_selector = self.config.get("title_selector", "a, h2, h3, .title, .job-title")
        url_selector = self.config.get("url_selector", "a[href]")
        location_selector = self.config.get("location_selector", ".location, .meta, .details")

        # Try to find job listings
        listing_container = soup.select_one(self.config.get("container_selector", "ul, table, .jobs-list, .postings"))
        if listing_container:
            listings = listing_container.find_all(lambda tag: tag.name in ["li", "tr", "div"] and tag.get("class", []) and any(
                c in " ".join(tag.get("class", [])) for c in ["job", "posting", "listing", "position", "row"]
            )) or listing_container.find_all(["li", "tr"])
        else:
            listings = soup.select(job_listing_selector)

        for listing in listings[:self.config.get("max_jobs", 50)]:
            job = {"title": None, "url": None, "location": None}

            # Extract title
            title_el = listing.select_one(title_selector) if title_selector else listing.find(["a", "h2", "h3"])
            if title_el:
                job["title"] = title_el.get_text(strip=True)
                if title_el.name == "a" and title_el.get("href"):
                    job["url"] = urljoin(base_url, title_el["href"])
                elif title_el.find("a"):
                    a_tag = title_el.find("a")
                    if a_tag and a_tag.get("href"):
                        job["url"] = urljoin(base_url, a_tag["href"])

            # Extract URL from link if not found
            if not job["url"] and url_selector:
                link_el = listing.select_one(url_selector)
                if link_el and link_el.get("href"):
                    job["url"] = urljoin(base_url, link_el["href"])

            # Extract location
            if location_selector:
                loc_el = listing.select_one(location_selector)
                if loc_el:
                    job["location"] = loc_el.get_text(strip=True)

            if job.get("title"):
                raw_jobs.append(job)

        return raw_jobs

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse generic job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            title = job.get("title", "")
            location = job.get("location", "")
            is_remote = "remote" in location.lower() if location else False

            # Generate external_id from URL or title hash
            job_url = job.get("url", "")
            if job_url:
                external_id = f"generic_{hashlib.md5(job_url.encode()).hexdigest()[:12]}"
            else:
                external_id = f"generic_{hashlib.md5(title.encode()).hexdigest()[:12]}"

            normalized = {
                "external_id": external_id,
                "title": title.strip() if title else "Unknown Position",
                "company_name": self.config.get("company_name", "Unknown Company"),
                "company_description": self.config.get("company_description", None),
                "company_url": self.config.get("company_url", None),
                "company_logo": self.config.get("company_logo", None),
                "location": location.strip() if location else None,
                "location_type": "remote" if is_remote else None,
                "is_remote": is_remote,
                "remote_type": "fully_remote" if is_remote else None,
                "description": job.get("description", None),
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
                "employment_type": self.config.get("employment_type", "full_time"),
                "industry": self.config.get("industry", None),
                "function": None,
                "department": None,
                "job_url": job_url,
                "apply_url": job_url,
                "posted_at": job.get("posted_date", None),
                "status": "active",
                "raw_data": job,
            }
            parsed.append(normalized)

        return parsed
