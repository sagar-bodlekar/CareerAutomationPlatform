"""Content assembler — converts profile data into structured resume content."""

from datetime import date


class ContentAssembler:
    """Assembles structured resume content from profile data."""

    def __init__(self) -> None:
        pass

    def from_profile(self, profile_data: dict) -> dict:
        """Convert profile data (from Profile Service) into resume content.

        Args:
            profile_data: The full profile dict from Profile Service.

        Returns:
            Structured resume content dict suitable for template rendering.
        """
        content = {
            "name": self._extract_name(profile_data),
            "title": profile_data.get("headline") or "",
            "summary": profile_data.get("summary") or "",
            "contact": self._build_contact(profile_data),
            "skills": self._build_skills(profile_data.get("skills", [])),
            "flat_skills": [s["name"] for s in profile_data.get("skills", [])],
            "experiences": self._build_experiences(profile_data.get("work_experiences", [])),
            "education": self._build_education(profile_data.get("education", [])),
            "projects": self._build_projects(profile_data.get("projects", [])),
            "certifications": self._build_certifications(profile_data.get("certifications", [])),
        }
        return content

    def _extract_name(self, profile: dict) -> str:
        """Extract full name from profile data."""
        if pi := profile.get("personal_info"):
            return pi.get("full_name") or f"{pi.get('first_name', '')} {pi.get('last_name', '')}".strip()
        return ""

    def _build_contact(self, profile: dict) -> list[str]:
        """Build contact info list."""
        contact = []
        if pi := profile.get("personal_info"):
            if pi.get("email"):
                contact.append(pi["email"])
            if pi.get("phone"):
                contact.append(pi["phone"])
            if pi.get("city") or pi.get("country"):
                parts = filter(None, [pi.get("city"), pi.get("country")])
                contact.append(", ".join(parts))
        for link in profile.get("social_links", []):
            if link.get("url"):
                contact.append(link["url"])
        return contact

    def _build_skills(self, skills: list[dict]) -> dict[str, list[dict]]:
        """Group skills by category."""
        grouped: dict[str, list[dict]] = {}
        for s in skills:
            cat = s.get("category") or "Other"
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append({
                "name": s["name"],
                "proficient": s.get("proficiency") in ("advanced", "expert"),
            })
        return grouped

    def _build_experiences(self, experiences: list[dict]) -> list[dict]:
        """Build experience entries with date ranges."""
        result = []
        for exp in experiences:
            start = self._parse_date(exp.get("start_date"))
            end = self._parse_date(exp.get("end_date"))
            date_range = self._format_date_range(start, end, exp.get("is_current", False))
            result.append({
                "company_name": exp["company_name"],
                "job_title": exp["job_title"],
                "date_range": date_range,
                "description": exp.get("description", ""),
                "achievements": exp.get("achievements", []),
                "skills_used": exp.get("skills_used", []),
            })
        return result

    def _build_education(self, education: list[dict]) -> list[dict]:
        """Build education entries."""
        result = []
        for edu in education:
            start = self._parse_date(edu.get("start_date"))
            end = self._parse_date(edu.get("end_date"))
            date_range = self._format_date_range(start, end, edu.get("is_current", False))
            result.append({
                "institution": edu["institution"],
                "degree": edu.get("degree", ""),
                "field_of_study": edu.get("field_of_study", ""),
                "date_range": date_range,
                "description": edu.get("description", ""),
            })
        return result

    def _build_projects(self, projects: list[dict]) -> list[dict]:
        """Build project entries."""
        result = []
        for p in projects:
            start = self._parse_date(p.get("start_date"))
            end = self._parse_date(p.get("end_date"))
            date_range = self._format_date_range(start, end, p.get("is_current", False))
            result.append({
                "name": p["name"],
                "description": p.get("description", ""),
                "technologies": p.get("technologies", []),
                "date_range": date_range,
                "highlights": p.get("highlights", []),
            })
        return result

    def _build_certifications(self, certifications: list[dict]) -> list[dict]:
        """Build certification entries."""
        result = []
        for c in certifications:
            result.append({
                "name": c["name"],
                "issuer": c.get("issuer", ""),
                "issue_date": str(c.get("issue_date", "")) if c.get("issue_date") else "",
            })
        return result

    def _parse_date(self, date_str: str | None) -> date | None:
        """Parse a date string if present."""
        if not date_str:
            return None
        try:
            if isinstance(date_str, str):
                return date.fromisoformat(date_str)
            if isinstance(date_str, date):
                return date_str
        except (ValueError, TypeError):
            return None
        return None

    def _format_date_range(
        self, start: date | None, end: date | None, is_current: bool
    ) -> str:
        """Format a date range like 'Jan 2020 - Present' or '2018 - 2021'."""
        def fmt(d: date | None) -> str:
            if d is None:
                return ""
            return d.strftime("%b %Y") if d else ""

        start_str = fmt(start) if start else ""
        end_str = "Present" if is_current else fmt(end) if end else ""
        if start_str and end_str:
            return f"{start_str} - {end_str}"
        if start_str:
            return start_str
        return ""
