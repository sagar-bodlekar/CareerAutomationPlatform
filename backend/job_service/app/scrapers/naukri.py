"""Naukri.com job scraper."""

import hashlib
import re
from typing import Optional

import httpx

from .base import JobScraper, ScrapeError


class NaukriScraper(JobScraper):
    """Scrapes job listings from Naukri.com."""

    SEARCH_URL = "https://www.naukri.com/jobapi/v4/search"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    @property
    def source_name(self) -> str:
        return "naukri"

    async def fetch(self) -> list[dict]:
        """Fetch jobs from Naukri API."""
        headers = {
            "User-Agent": self.config.get("user_agent", self.USER_AGENT),
            "Accept": "application/json",
            "Referer": "https://www.naukri.com/",
            "AppId": "105",
            "SystemId": "Naukri",
        }
        params = {
            "q": self.config.get("query", "software engineer"),
            "location": self.config.get("location", ""),
            "noOfResults": self.config.get("limit", 20),
            "searchType": "adv",
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

        # Extract job details from response
        job_details = data.get("jobDetails", [])
        return job_details if isinstance(job_details, list) else []

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse Naukri job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            title = job.get("title", "") or job.get("jobTitle", "")
            company = job.get("companyName", "") or job.get("company", "")
            jd = job.get("jobDescription", "") or job.get("description", "")

            # Extract skills from job description
            skills = self._extract_skills(jd)

            # Parse location
            loc = job.get("location", "") or job.get("place", "")
            is_remote = "remote" in loc.lower() or "work from home" in loc.lower()

            # Parse salary
            salary_min, salary_max = self._parse_salary(
                job.get("salary", "") or job.get("annualSalary", "")
            )

            external_id = job.get("jobId", "") or job.get("id", "")
            external_id = f"naukri_{external_id}" if external_id else None

            normalized = {
                "external_id": external_id,
                "title": title.strip() or "Unknown Position",
                "company_name": company.strip() or "Unknown Company",
                "company_description": None,
                "company_url": None,
                "company_logo": job.get("companyLogo", ""),
                "location": loc.strip() if loc else None,
                "location_type": "remote" if is_remote else "onsite",
                "is_remote": is_remote,
                "remote_type": "fully_remote" if is_remote else None,
                "description": jd.strip() if jd else None,
                "requirements": None,
                "responsibilities": None,
                "required_skills": skills,
                "nice_to_have_skills": None,
                "experience_min_years": job.get("minExperience", None) or self._parse_experience(
                    job.get("experience", "")
                )[0],
                "experience_max_years": job.get("maxExperience", None) or self._parse_experience(
                    job.get("experience", "")
                )[1],
                "experience_level": None,
                "education_required": job.get("education", None),
                "degree_preferred": None,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "INR",
                "salary_period": "yearly",
                "salary_visible": salary_min is not None,
                "employment_type": "full_time",
                "industry": job.get("industry", None),
                "function": job.get("functionalArea", None),
                "department": None,
                "job_url": job.get("url", "") or job.get("jobURL", ""),
                "apply_url": job.get("applyUrl", "") or job.get("url", ""),
                "posted_at": job.get("postedDate", None) or job.get("createdDate", None),
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
