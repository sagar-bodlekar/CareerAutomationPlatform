"""Wellfound (AngelList) job scraper.

IMPORTANT: Wellfound no longer provides public API access. Their website is
protected by Cloudflare (returns 403 to automated requests).

This scraper attempts multiple approaches:
1. HTML scraping of wellfound.com/jobs (behind Cloudflare, likely fails)
2. Legacy AngelList API (api.angel.co/1/jobs - likely deprecated)

If all approaches fail, the scraper logs the error and returns empty.
For reliable Wellfound data, consider using a third-party data provider or
configuring the GenericCareerPageScraper with a company's specific career page.
"""

import hashlib
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .base import JobScraper, ScrapeError


class WellfoundScraper(JobScraper):
    """Scrapes startup job listings from Wellfound (AngelList).

    Note: Wellfound has deprecated their public APIs and uses Cloudflare
    bot protection. This scraper attempts HTML scraping as a fallback
    but may not work reliably.
    """

    SEARCH_URL = "https://wellfound.com/jobs"
    API_URL = "https://api.angel.co/1/jobs"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @property
    def source_name(self) -> str:
        return "wellfound"

    async def fetch(self) -> list[dict]:
        """Fetch jobs from Wellfound.

        Tries HTML scraping first (wellfound.com/jobs), then falls back
        to the legacy AngelList API (api.angel.co/1/jobs).
        """
        headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENT),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://wellfound.com/",
        }
        timeout = self.config.get("timeout", 30)

        # Attempt 1: HTML scrape of the main jobs page
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                params = {
                    "page": self.config.get("page", 1),
                    "remote": "true" if self.config.get("remote_only", False) else "",
                    "role": self.config.get("role", ""),
                }
                response = await client.get(self.SEARCH_URL, headers=headers, params=params)
                response.raise_for_status()

                # If we got HTML (not blocked by Cloudflare), parse it
                content_type = response.headers.get("content-type", "")
                if "html" in content_type:
                    return self._parse_html(response.text)

                # If we got JSON (unlikely but possible)
                if "json" in content_type:
                    data = response.json()
                    jobs = data.get("jobs", []) or data.get("data", []) or data
                    if isinstance(jobs, list):
                        return jobs

            except httpx.HTTPStatusError as e:
                # 403 = blocked by Cloudflare, try legacy API as fallback
                if e.response.status_code != 403:
                    raise ScrapeError(
                        f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                        self.source_name,
                    )
            except httpx.TimeoutException:
                raise ScrapeError("Request timed out", self.source_name)
            except Exception as e:
                raise ScrapeError(f"Fetch failed: {e}", self.source_name)

        # Attempt 2: Legacy AngelList API (likely deprecated)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                api_params = {
                    "page": self.config.get("page", 1),
                    "per_page": self.config.get("limit", 20),
                }
                response = await client.get(self.API_URL, headers={
                    "User-Agent": self.USER_AGENT,
                    "Accept": "application/json",
                }, params=api_params)
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", []) if isinstance(data, dict) else data
                return jobs if isinstance(jobs, list) else []
            except Exception:
                pass  # Both attempts failed

        raise ScrapeError(
            "Wellfound is not accessible: both HTML page (behind Cloudflare) "
            "and legacy API (deprecated) failed. "
            "Consider using GenericCareerPageScraper for specific company career pages.",
            self.source_name,
        )

    def _parse_html(self, html: str) -> list[dict]:
        """Parse Wellfound HTML page into raw job dicts."""
        soup = BeautifulSoup(html, "html.parser")
        raw_jobs = []

        # Look for job cards or script tags with JSON data
        script_tags = soup.find_all("script", type="application/json")
        for script in script_tags:
            try:
                import json as json_lib
                data = json_lib.loads(script.string)
                if isinstance(data, dict):
                    # Look for job listings in common Next.js data structures
                    for key in ["jobs", "listings", "positions", "props"]:
                        vals = data.get(key, {}) or data.get("pageProps", {}).get(key, {})
                        if isinstance(vals, list):
                            raw_jobs.extend(vals)
            except (json_lib.JSONDecodeError, TypeError):
                continue

        if raw_jobs:
            return raw_jobs

        # Fallback: look for job card elements
        job_cards = (
            soup.select("div[class*='job']")
            or soup.select("a[class*='job']")
            or soup.select("div[class*='listing']")
        )
        for card in job_cards:
            job = {}
            title_el = card.select_one("h2, h3, .title, [class*='title']")
            if title_el:
                job["title"] = title_el.get_text(strip=True)
            company_el = card.select_one("[class*='company'], [class*='startup']")
            if company_el:
                job["company_name"] = company_el.get_text(strip=True)
            if job.get("title"):
                raw_jobs.append(job)

        return raw_jobs

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse Wellfound job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            title = job.get("title", "") or job.get("position", "") or job.get("role", "")
            company_data = job.get("startup", {}) or job.get("company", {})
            if isinstance(company_data, dict):
                company_name = company_data.get("name", "") or job.get("company_name", "") or job.get("company", "")
                company_logo = company_data.get("logo_url", "") or company_data.get("logo", "")
                company_url = company_data.get("company_url", "") or company_data.get("url", "")
                company_desc = company_data.get("description", "")
                industry = company_data.get("market", "") or company_data.get("industry", "")
            else:
                company_name = job.get("company_name", "") or job.get("company", "")
                company_logo = ""
                company_url = ""
                company_desc = None
                industry = None

            jd = job.get("description", "") or job.get("job_description", "") or job.get("text", "")

            # Parse skills from description
            skills = self._extract_skills(jd)

            # Location
            location = job.get("location", "") or job.get("city", "") or job.get("office", "")
            remote = job.get("remote", False) or job.get("remote_possible", False) or job.get("remotely", False)

            # Salary
            salary_min = job.get("salary_min", None) or job.get("min_salary", None) or job.get("salary_low", None)
            salary_max = job.get("salary_max", None) or job.get("max_salary", None) or job.get("salary_high", None)
            if salary_min:
                try:
                    salary_min = float(salary_min)
                except (ValueError, TypeError):
                    salary_min = None
            if salary_max:
                try:
                    salary_max = float(salary_max)
                except (ValueError, TypeError):
                    salary_max = None

            # Experience
            exp_min = job.get("experience_min", None) or job.get("min_years", None)
            if exp_min:
                try:
                    exp_min = int(exp_min)
                except (ValueError, TypeError):
                    exp_min = None

            external_id = job.get("id", "") or job.get("job_id", "") or job.get("slug", "")
            external_id = f"wellfound_{external_id}" if external_id else None

            normalized = {
                "external_id": external_id,
                "title": title.strip() if title else "Unknown Position",
                "company_name": company_name.strip() if company_name else "Unknown Company",
                "company_description": company_desc,
                "company_url": company_url,
                "company_logo": company_logo,
                "location": location.strip() if location else None,
                "location_type": "remote" if remote else "onsite",
                "is_remote": bool(remote),
                "remote_type": "fully_remote" if remote else None,
                "description": jd.strip() if jd else None,
                "requirements": None,
                "responsibilities": None,
                "required_skills": skills if skills else None,
                "nice_to_have_skills": None,
                "experience_min_years": exp_min,
                "experience_max_years": None,
                "experience_level": None,
                "education_required": None,
                "degree_preferred": None,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "USD",
                "salary_period": "yearly",
                "salary_visible": salary_min is not None,
                "employment_type": "full_time",
                "industry": industry,
                "function": job.get("function", None),
                "department": job.get("department", None),
                "job_url": job.get("url", "") or job.get("job_url", "") or f"https://wellfound.com/jobs/{job.get('id', '')}",
                "apply_url": job.get("apply_url", "") or job.get("url", "") or job.get("hostedUrl", ""),
                "posted_at": job.get("created_at", None) or job.get("posted_date", None) or job.get("date", None),
                "status": "active",
                "raw_data": job,
            }
            parsed.append(normalized)

        return parsed

    def _extract_skills(self, text: str) -> list[str]:
        """Extract skill keywords from job description."""
        if not text:
            return []
        skills = set()
        tech_keywords = [
            r"Python", r"Java(?:Script)?", r"TypeScript", r"React", r"Angular",
            r"Vue\.?js", r"Node\.?js", r"Go(lang)?", r"Rust", r"Swift",
            r"Kotlin", r"SQL", r"PostgreSQL", r"MySQL", r"MongoDB",
            r"Redis", r"Docker", r"Kubernetes", r"AWS", r"GCP",
            r"TensorFlow", r"PyTorch", r"Machine Learning",
        ]
        for pattern in tech_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                skills.add(pattern.replace(r"\\.", "."))
        return sorted(skills)
