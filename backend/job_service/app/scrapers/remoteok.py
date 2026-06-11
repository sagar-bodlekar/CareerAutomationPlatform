"""RemoteOK job scraper."""

import hashlib
from typing import Optional

import httpx

from .base import JobScraper, ScrapeError


class RemoteOKScraper(JobScraper):
    """Scrapes remote job listings from RemoteOK."""

    BASE_URL = "https://remoteok.com/api"
    USER_AGENT = "Mozilla/5.0 (compatible; CareerPlatform/1.0)"

    @property
    def source_name(self) -> str:
        return "remoteok"

    async def fetch(self) -> list[dict]:
        """Fetch jobs from RemoteOK API."""
        headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENT),
        }
        timeout = self.config.get("timeout", 30)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(self.BASE_URL, headers=headers)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                raise ScrapeError(
                    f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                    self.source_name,
                )
            except httpx.TimeoutException:
                raise ScrapeError("Request timed out", self.source_name)
            except Exception as e:
                raise ScrapeError(f"Fetch failed: {e}", self.source_name)

        # RemoteOK API returns a JSON array; first element is typically metadata
        if isinstance(data, list) and len(data) > 0:
            # Skip metadata element if present (has slug starting with '_')
            raw_jobs = [j for j in data if isinstance(j, dict) and not j.get("slug", "").startswith("_")]
            return raw_jobs

        return []

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse RemoteOK job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            # Build external_id from job URL slug
            slug = job.get("slug", "")
            external_id = f"remoteok_{slug}" if slug else None

            # Extract skills from tags
            tags = job.get("tags", [])
            skills = [tag.strip() for tag in tags if tag and isinstance(tag, str)] if tags else []

            # Build salary range
            salary_min = None
            salary_max = None
            salary_currency = "USD"
            salary_str = job.get("salary", "")
            if salary_str and isinstance(salary_str, str):
                # Parse ranges like "$100k-$150k" or "$80k"
                import re
                amounts = re.findall(r"\d+", salary_str.replace(",", ""))
                if len(amounts) >= 2:
                    salary_min = float(amounts[0]) * 1000
                    salary_max = float(amounts[1]) * 1000
                elif len(amounts) == 1:
                    salary_min = float(amounts[0]) * 1000

            normalized = {
                "external_id": external_id,
                "title": job.get("position", "").strip() or "Unknown Position",
                "company_name": job.get("company", "").strip() or "Unknown Company",
                "company_description": job.get("description", ""),
                "company_url": job.get("url", ""),
                "company_logo": job.get("logo", ""),
                "location": "Remote",
                "location_type": "remote",
                "is_remote": True,
                "remote_type": "fully_remote",
                "description": job.get("description", ""),
                "requirements": job.get("requirements", ""),
                "required_skills": skills,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": salary_currency,
                "salary_period": "yearly",
                "salary_visible": salary_min is not None,
                "employment_type": "full_time",
                "job_url": f"https://remoteok.com/remote-jobs/{slug}" if slug else None,
                "apply_url": job.get("url", ""),
                "posted_at": job.get("date", None),
                "status": "active",
                "raw_data": job,
            }
            parsed.append(normalized)

        return parsed
