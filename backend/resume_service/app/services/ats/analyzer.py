"""ATS Analyzer — parses job descriptions and analyzes resume compatibility."""

from app.services.ats.keyword_extractor import KeywordExtractor


class ATSAnalyzer:
    """Analyzes job descriptions and compares against resume content."""

    def __init__(self) -> None:
        self.keyword_extractor = KeywordExtractor()

    def analyze_job_description(self, job_description: str) -> dict:
        """Analyze a job description and extract structured requirements.

        Returns:
            Dict with ``keywords``, ``required_skills``, ``experience_years``.
        """
        keywords = self.keyword_extractor.extract_keywords(job_description)
        required_skills = self.keyword_extractor.extract_required_skills(job_description)
        experience_years = self.keyword_extractor.extract_experience_years(job_description)

        return {
            "keywords": keywords,
            "required_skills": required_skills,
            "experience_years": experience_years,
        }

    def analyze_resume_content(self, content: dict) -> dict:
        """Analyze resume content and extract structured data.

        Returns:
            Dict with ``skills``, ``experience_years``, ``sections_present``.
        """
        skills = [s["name"] for s in content.get("skills", {}).values()]
        flat_skills = content.get("flat_skills", [])

        sections = []
        if content.get("summary"):
            sections.append("summary")
        if content.get("experiences"):
            sections.append("experience")
        if content.get("education"):
            sections.append("education")
        if content.get("skills"):
            sections.append("skills")
        if content.get("projects"):
            sections.append("projects")
        if content.get("certifications"):
            sections.append("certifications")

        return {
            "skills": list(set(skills + flat_skills)),
            "experience_years": self._estimate_years(content.get("experiences", [])),
            "sections_present": sections,
        }

    def _estimate_years(self, experiences: list[dict]) -> float:
        """Estimate total years of experience from work history."""
        total_years = 0.0
        for exp in experiences:
            # Simple heuristic: assume each role is at least 1 year
            total_years += 1.0
        return total_years
