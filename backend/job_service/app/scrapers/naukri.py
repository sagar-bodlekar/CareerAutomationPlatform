"""Naukri.com job scraper.

Note: Naukri's public API (jobapi/v4/search) was deprecated. Naukri now uses
client-side rendering (SPA), so HTML-based scraping with BeautifulSoup cannot
extract job data from the static page.

To scrape Naukri, you would need:
1. A headless browser (Playwright/Selenium) to execute JavaScript
2. Or access to Naukri's internal API (requires authentication tokens)
3. Or a third-party data provider that aggregates Naukri jobs

For now, the scraper attempts HTML scraping but will likely return 0 jobs.
Consider using a third-party aggregator or removing this source.
"""

import hashlib
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .base import JobScraper, ScrapeError


class NaukriScraper(JobScraper):
    """Scrapes job listings from Naukri.com via HTML scraping."""

    SEARCH_URL = "https://www.naukri.com/{query}-jobs-in-{location}"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @property
    def source_name(self) -> str:
        return "naukri"

    async def fetch(self) -> list[dict]:
        """Fetch jobs by scraping Naukri search results HTML."""
        query = self.config.get("query", "software engineer")
        location = self.config.get("location", "india")
        # Sanitize query: lowercase, replace spaces with hyphens, remove special chars
        query_slug = re.sub(r"[^a-z0-9-]", "", query.lower().replace(" ", "-"))
        location_slug = re.sub(r"[^a-z0-9-]", "", location.lower().replace(" ", "-"))
        if not query_slug:
            query_slug = "software-engineer"
        if not location_slug:
            location_slug = "india"
        # Build URL like https://www.naukri.com/python-jobs-in-bangalore
        search_url = f"https://www.naukri.com/{query_slug}-jobs-in-{location_slug}"

        headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENT),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.naukri.com/",
        }
        timeout = self.config.get("timeout", 30)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                response = await client.get(search_url, headers=headers)
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

            return self._parse_html(response.text)

    def _parse_html(self, html: str) -> list[dict]:
        """Parse Naukri search results HTML into raw job dicts."""
        soup = BeautifulSoup(html, "html.parser")
        raw_jobs = []

        # Try multiple selectors for job cards (Naukri changes classes frequently)
        job_cards = (
            soup.select("article.jobTuple")
            or soup.select("div.jobListing")
            or soup.select("div[class*='jobTuple']")
            or soup.select("section[class*='job']")
            or soup.select("div[class*='listing']")
            or soup.select("div[class*='card']")
        )

        if not job_cards:
            # Naukri uses client-side rendering - no job cards found in HTML
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "Naukri HTML scraping: no job cards found. "
                "Naukri uses client-side JavaScript rendering (SPA), "
                "so job data is not present in the static HTML. "
                "Consider using a headless browser or a third-party aggregator."
            )
            return []

        for card in job_cards[:self.config.get("limit", 20)]:
            job = {}

            # Title
            title_el = (
                card.select_one("a.title")
                or card.select_one("a[class*='title']")
                or card.select_one("h2 a")
                or card.select_one("a[href*='job-detail']")
            )
            if title_el:
                job["title"] = title_el.get_text(strip=True)
                job["url"] = title_el.get("href", "")
                if job["url"] and not job["url"].startswith("http"):
                    job["url"] = f"https://www.naukri.com{job['url']}"

            # Company
            company_el = (
                card.select_one("a.company")
                or card.select_one("a[class*='company']")
                or card.select_one("a[class*='subTitle']")
            )
            if company_el:
                job["company_name"] = company_el.get_text(strip=True)

            # Location
            loc_el = (
                card.select_one("span[class*='location']")
                or card.select_one("li[class*='location']")
                or card.select_one("span[class*='loc']")
            )
            if loc_el:
                job["location"] = loc_el.get_text(strip=True)

            # Salary
            salary_el = (
                card.select_one("span[class*='salary']")
                or card.select_one("li[class*='salary']")
            )
            if salary_el:
                job["salary"] = salary_el.get_text(strip=True)

            # Experience
            exp_el = (
                card.select_one("span[class*='experience']")
                or card.select_one("li[class*='exp']")
            )
            if exp_el:
                job["experience"] = exp_el.get_text(strip=True)

            # Skills/tags
            skill_els = card.select("span[class*='skill']") or card.select("a[class*='skill']") or card.select("span.tag")
            if skill_els:
                job["skills"] = [s.get_text(strip=True) for s in skill_els if s.get_text(strip=True)]

            # Posted date
            date_el = (
                card.select_one("span[class*='date']")
                or card.select_one("span[class*='time']")
                or card.select_one("span[class*='posted']")
            )
            if date_el:
                job["posted_date"] = date_el.get_text(strip=True)

            # Generate a deterministic ID from URL
            if job.get("url"):
                job["id"] = hashlib.md5(job["url"].encode()).hexdigest()[:12]

            if job.get("title"):
                raw_jobs.append(job)

        return raw_jobs

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse Naukri job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            title = job.get("title", "")
            company = job.get("company_name", "") or job.get("company", "")

            # Extract skills from tags
            skills = job.get("skills", [])
            # Also extract from any description text
            jd = job.get("description", "")
            if jd:
                skills_from_jd = self._extract_skills(jd)
                for s in skills_from_jd:
                    if s not in skills:
                        skills.append(s)

            # Parse location
            loc = job.get("location", "")
            is_remote = "remote" in loc.lower() or "work from home" in loc.lower() or "wfh" in loc.lower()

            # Parse salary
            salary_min, salary_max = self._parse_salary(
                job.get("salary", "")
            )

            external_id = job.get("id", "")
            external_id = f"naukri_{external_id}" if external_id else None

            normalized = {
                "external_id": external_id,
                "title": title.strip() or "Unknown Position",
                "company_name": company.strip() or "Unknown Company",
                "company_description": None,
                "company_url": None,
                "company_logo": None,
                "location": loc.strip() if loc else None,
                "location_type": "remote" if is_remote else "onsite",
                "is_remote": is_remote,
                "remote_type": "fully_remote" if is_remote else None,
                "description": jd.strip() if jd else None,
                "requirements": None,
                "responsibilities": None,
                "required_skills": skills if skills else None,
                "nice_to_have_skills": None,
                "experience_min_years": self._parse_experience(
                    job.get("experience", "")
                )[0],
                "experience_max_years": self._parse_experience(
                    job.get("experience", "")
                )[1],
                "experience_level": None,
                "education_required": None,
                "degree_preferred": None,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "INR",
                "salary_period": "yearly",
                "salary_visible": salary_min is not None,
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

    def _extract_skills(self, text: str) -> list[str]:
        """Extract skill keywords from job description text."""
        if not text:
            return []
        skills = set()
        tech_keywords = [
            r"Python", r"Java(?:Script)?", r"TypeScript", r"React", r"Angular",
            r"Vue\.?js", r"Node\.?js", r"\.NET", r"C#", r"Go(lang)?", r"Rust",
            r"SQL", r"PostgreSQL", r"MySQL", r"MongoDB", r"Redis", r"Docker",
            r"Kubernetes", r"AWS", r"Azure", r"GCP", r"CI/CD", r"Git",
            r"REST\s*API", r"GraphQL", r"Flask", r"Django", r"FastAPI",
            r"TensorFlow", r"PyTorch", r"Machine Learning", r"Deep Learning",
            r"Agile", r"Scrum", r"DevOps",
        ]
        for pattern in tech_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                skills.add(pattern.replace(r"\.", ".").replace(r"\s*", "").replace(r"\?", ""))
        return sorted(skills)

    def _parse_salary(self, salary_str: str) -> tuple[Optional[float], Optional[float]]:
        """Parse salary string like '6-12 Lacs PA' or '10L'."""
        if not salary_str or not isinstance(salary_str, str):
            return None, None
        amounts = re.findall(r"(\d+\.?\d*)", salary_str.replace(",", ""))
        if not amounts:
            return None, None
        multiplier = 1
        if "lac" in salary_str.lower() or "lakh" in salary_str.lower():
            multiplier = 100000
        elif "cr" in salary_str.lower() or "crore" in salary_str.lower():
            multiplier = 10000000
        values = [float(a) * multiplier for a in amounts]
        if len(values) >= 2:
            return min(values), max(values)
        return values[0], None

    def _parse_experience(self, exp_str: str) -> tuple[Optional[int], Optional[int]]:
        """Parse experience string like '3-5 yrs'."""
        if not exp_str or not isinstance(exp_str, str):
            return None, None
        amounts = re.findall(r"(\d+)", exp_str)
        if not amounts:
            return None, None
        values = [int(a) for a in amounts]
        if len(values) >= 2:
            return values[0], values[1]
        return values[0], None
