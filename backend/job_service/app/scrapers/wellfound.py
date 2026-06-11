"""Wellfound (AngelList) job scraper."""

import hashlib
import re
from typing import Optional

import httpx

from .base import JobScraper, ScrapeError


class WellfoundScraper(JobScraper):
    """Scrapes startup job listings from Wellfound (AngelList)."""

    API_URL = "https://api.angel.co/1/jobs"
    SEARCH_URL = "https://wellfound.com/api/v1/jobs/search"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @property
    def source_name(self) -> str:
        return "wellfound"

    async def fetch(self) -> list[dict]:
        """Fetch jobs from Wellfound API."""
        headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENT),
            "Accept": "application/json",
            "Referer": "https://wellfound.com/",
        }
        params = {
            "page": self.config.get("page", 1),
            "per_page": self.config.get("limit", 20),
            "remote": self.config.get("remote_only", False),
            "role": self.config.get("role", ""),
        }
        timeout = self.config.get("timeout", 30)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            try:
                response = await client.get(self.SEARCH_URL, headers=headers, params=params)
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

        jobs = data.get("jobs", []) or data.get("data", [])
        return jobs if isinstance(jobs, list) else []

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse Wellfound job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            # Handle different API response formats
            title = job.get("title", "") or job.get("role", "")
            company_data = job.get("startup", {}) or job.get("company", {})
            if isinstance(company_data, dict):
                company_name = company_data.get("name", "") or job.get("company_name", "")
                company_logo = company_data.get("logo_url", "") or company_data.get("logo", "")
                company_url = company_data.get("company_url", "") or company_data.get("url", "")
            else:
                company_name = job.get("company_name", "")
                company_logo = ""
                company_url = ""

            jd = job.get("description", "") or job.get("job_description", "")

            # Parse skills from description
            skills = self._extract_skills(jd)

            # Location
            location = job.get("location", "") or job.get("city", "")
            remote = job.get("remote", False) or job.get("remote_possible", False)

            # Salary
            salary_min = job.get("salary_min", None) or job.get("min_salary", None)
            salary_max = job.get("salary_max", None) or job.get("max_salary", None)
            if salary_min:
                salary_min = float(salary_min)
            if salary_max:
                salary_max = float(salary_max)

            # Equity
            equity_min = job.get("equity_min", None)
            equity_max = job.get("equity_max", None)

            # Experience
            exp_min = job.get("experience_min", None)
            if exp_min:
                try:
                    exp_min = int(exp_min)
                except (ValueError, TypeError):
                    exp_min = None

            external_id = job.get("id", "")
            external_id = f"wellfound_{external_id}" if external_id else None

            normalized = {
                "external_id": external_id,
                "title": title.strip() or "Unknown Position",
                "company_name": company_name.strip() or "Unknown Company",
                "company_description": company_data.get("description", "") if isinstance(company_data, dict) else None,
                "company_url": company_url,
                "company_logo": company_logo,
                "location": location.strip() if location else None,
                "location_type": "remote" if remote else "onsite",
                "is_remote": bool(remote),
                "remote_type": "fully_remote" if remote else None,
                "description": jd.strip() if jd else None,
                "requirements": None,
                "responsibilities": None,
                "required_skills": skills,
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
                "industry": company_data.get("market", "") if isinstance(company_data, dict) else None,
                "function": None,
                "department": None,
                "job_url": job.get("url", "") or f"https://wellfound.com/jobs/{job.get('id', '')}",
                "apply_url": job.get("apply_url", "") or job.get("url", ""),
                "posted_at": job.get("created_at", None) or job.get("posted_date", None),
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
