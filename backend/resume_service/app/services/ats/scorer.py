"""ATS Scorer — scores resume compatibility with a job description."""

from app.services.ats.keyword_extractor import KeywordExtractor


class ATSScorer:
    """Scores resume compatibility with job requirements.

    Scoring dimensions:
    - Keyword match (40%): presence of job keywords in resume
    - Format/Sections (20%): presence of expected resume sections
    - Experience relevance (20%): years experience vs requirement
    - Skills alignment (20%): overlap between required and present skills
    """

    def __init__(self) -> None:
        self.keyword_extractor = KeywordExtractor()

    def score(
        self,
        resume_skills: list[str],
        resume_sections: list[str],
        resume_years: float,
        job_description: str,
    ) -> dict:
        """Compute ATS score for a resume against a job description.

        Args:
            resume_skills: List of skills present in the resume.
            resume_sections: List of sections present in the resume.
            resume_years: Estimated total years of experience.
            job_description: The target job description text.

        Returns:
            Dict with ``overall_score`` and individual dimension scores.
        """
        analysis = self.keyword_extractor.extract_keywords(job_description)
        required_skills = self.keyword_extractor.extract_required_skills(job_description)

        # 1. Keyword match score (40%)
        resume_text_set = set(s.lower() for s in resume_skills)
        job_keywords_set = set(k.lower() for k in analysis)
        if job_keywords_set:
            keyword_matches = resume_text_set & job_keywords_set
            keyword_score = (len(keyword_matches) / len(job_keywords_set)) * 100
        else:
            keyword_score = 0

        # 2. Section coverage (20%)
        expected_sections = {"summary", "experience", "education", "skills"}
        present_sections = set(s.lower() for s in resume_sections)
        if expected_sections:
            section_coverage = len(present_sections & expected_sections)
            section_score = (section_coverage / len(expected_sections)) * 100
        else:
            section_score = 0

        # 3. Experience relevance (20%)
        job_exp_years = self.keyword_extractor.extract_experience_years(job_description)
        if job_exp_years and job_exp_years > 0:
            exp_ratio = min(resume_years / job_exp_years, 2.0)  # Cap at 2x
            experience_score = min(exp_ratio * 50, 100)  # 50% at match, 100% at 2x
        else:
            experience_score = 75  # Default if no years specified

        # 4. Skills alignment (20%)
        if required_skills:
            required_set = set(s.lower() for s in required_skills)
            matched_skills = required_set & resume_text_set
            missing_skills = required_set - resume_text_set
            skills_score = (len(matched_skills) / len(required_set)) * 100
        else:
            matched_skills = set()
            missing_skills = set()
            skills_score = 50

        # Weighted overall score
        overall = (
            keyword_score * 0.40
            + section_score * 0.20
            + experience_score * 0.20
            + skills_score * 0.20
        )

        return {
            "overall_score": round(overall, 1),
            "keyword_score": round(keyword_score, 1),
            "section_score": round(section_score, 1),
            "experience_score": round(experience_score, 1),
            "skills_score": round(skills_score, 1),
            "matched_keywords": sorted(matched_skills),
            "missing_keywords": sorted(missing_skills),
            "total_keywords": len(job_keywords_set),
        }
