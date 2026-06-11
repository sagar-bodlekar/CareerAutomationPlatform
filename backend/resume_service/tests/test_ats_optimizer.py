"""Tests for ATS analysis engine."""

import pytest

from app.services.ats.keyword_extractor import KeywordExtractor
from app.services.ats.scorer import ATSScorer
from app.services.ats.recommendation_engine import ATSRecommendationEngine
from app.services.ats.optimizer import ATSOptimizer


class TestKeywordExtractor:
    """Test keyword extraction from job descriptions."""

    def setup_method(self):
        self.extractor = KeywordExtractor()

    def test_extract_keywords(self):
        jd = "Looking for a Python developer with React experience and PostgreSQL knowledge."
        keywords = self.extractor.extract_keywords(jd)
        assert "Python" in keywords
        assert "React" in keywords
        assert "PostgreSQL" in keywords

    def test_extract_required_skills(self):
        jd = "Requirements: Python, React, Docker, Kubernetes. 5+ years experience."
        skills = self.extractor.extract_required_skills(jd)
        assert len(skills) > 0

    def test_extract_experience_years(self):
        jd = "Requires 5+ years of experience in software development."
        years = self.extractor.extract_experience_years(jd)
        assert years == 5

    def test_extract_experience_years_alternate(self):
        jd = "Experience of 3 years in Python development."
        years = self.extractor.extract_experience_years(jd)
        assert years == 3

    def test_extract_experience_years_none(self):
        jd = "Looking for a talented developer."
        years = self.extractor.extract_experience_years(jd)
        assert years is None


class TestATSScorer:
    """Test ATS scoring."""

    def setup_method(self):
        self.scorer = ATSScorer()

    def test_score_perfect_match(self):
        result = self.scorer.score(
            resume_skills=["Python", "React", "PostgreSQL", "Docker"],
            resume_sections=["summary", "experience", "education", "skills"],
            resume_years=6.0,
            job_description="Python developer with React and PostgreSQL, 5+ years exp.",
        )
        assert result["overall_score"] > 50
        assert len(result["matched_keywords"]) > 0

    def test_score_no_match(self):
        result = self.scorer.score(
            resume_skills=["Ruby", "Rails"],
            resume_sections=["summary"],
            resume_years=1.0,
            job_description="Python developer with React, 5+ years exp, Docker, Kubernetes.",
        )
        assert result["overall_score"] < 50
        assert len(result["missing_keywords"]) > 0

    def test_keyword_score_dimension(self):
        result = self.scorer.score(
            resume_skills=["Python", "React"],
            resume_sections=["summary", "experience", "education", "skills"],
            resume_years=5.0,
            job_description="Python developer with React and TypeScript.",
        )
        assert "keyword_score" in result
        assert "section_score" in result
        assert "experience_score" in result
        assert "skills_score" in result

    def test_empty_job_description(self):
        result = self.scorer.score(
            resume_skills=["Python"],
            resume_sections=["summary"],
            resume_years=5.0,
            job_description="",
        )
        assert result["overall_score"] >= 0


class TestATSRecommendationEngine:
    """Test recommendation generation."""

    def setup_method(self):
        self.engine = ATSRecommendationEngine()

    def test_missing_keywords_recommendation(self):
        scores = {
            "missing_keywords": ["Python", "React"],
            "keyword_score": 20,
            "section_score": 100,
            "experience_score": 100,
            "skills_score": 50,
        }
        content = {
            "summary": "Developer",
            "experiences": [{"company_name": "Acme", "job_title": "Dev"}],
            "education": [{"institution": "MIT"}],
            "skills": {},
            "projects": [],
        }
        recommendations = self.engine.generate_recommendations(scores, content, "")
        assert len(recommendations) > 0
        assert any("Python" in r for r in recommendations)


class TestATSOptimizer:
    """Test ATS optimizer integration."""

    @pytest.mark.asyncio
    async def test_analyze_and_optimize(self):
        optimizer = ATSOptimizer()
        result = await optimizer.analyze_and_optimize(
            resume_content={
                "name": "John Doe",
                "summary": "Senior developer",
                "flat_skills": ["Python", "React"],
                "skills": {},
                "experiences": [],
                "education": [],
                "projects": [],
                "certifications": [],
            },
            job_description="Looking for Python developer with React, 5+ years.",
        )
        assert "score" in result
        assert "score_breakdown" in result
        assert "recommendations" in result
        assert "missing_keywords" in result
        assert "matched_keywords" in result
