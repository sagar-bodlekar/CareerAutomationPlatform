"""Tests for prompt template engine."""

import tempfile
from pathlib import Path

import pytest


class TestPromptEngine:
    """Tests for PromptEngine."""

    @pytest.fixture
    def engine(self):
        """Create prompt engine pointing to real templates."""
        from app.services.prompt_engine import PromptEngine
        return PromptEngine()

    def test_list_templates(self, engine):
        """Should list available prompt templates."""
        templates = engine.list_templates()
        assert len(templates) > 0
        # Should find resume optimizer templates
        resume_templates = [t for t in templates if "resume_optimizer" in t]
        assert len(resume_templates) > 0

    def test_render_ats_optimization(self, engine):
        """Should render ATS optimization template."""
        content = engine.render(
            "resume_optimizer/ats_optimization.j2",
            {
                "job_description": "Looking for a Python developer",
                "resume_content": "Experienced Python developer",
                "target_role": "Senior Python Developer",
            },
        )
        assert "Python" in content
        assert "ATS" in content
        assert "job_description" not in content  # Variable should be replaced

    def test_render_match_scoring(self, engine):
        """Should render match scoring template."""
        content = engine.render(
            "job_matcher/match_scoring.j2",
            {
                "skills": ["Python", "React"],
                "experience_summary": "5 years",
                "education_summary": "BS Computer Science",
                "location": "Remote",
                "preferred_roles": "Software Engineer",
                "job_title": "Senior Software Engineer",
                "company_name": "TechCorp",
                "required_skills": ["Python", "React", "AWS"],
                "nice_to_have_skills": ["Docker"],
                "experience_required": "3-5 years",
                "education_required": "BS",
                "job_location": "Remote",
                "employment_type": "full_time",
            },
        )
        assert "Python" in content
        assert "TechCorp" in content

    def test_render_cover_letter(self, engine):
        """Should render cover letter template."""
        content = engine.render(
            "outreach/cover_letter.j2",
            {
                "candidate_name": "John Doe",
                "current_role": "Software Engineer",
                "skills": ["Python", "React"],
                "achievements": ["Led team of 5"],
                "company_name": "TechCorp",
                "industry": "Technology",
                "company_description": "A great company",
                "job_title": "Senior Engineer",
                "job_description": "Looking for a senior engineer",
                "required_skills": ["Python"],
                "tone": "professional",
            },
        )
        assert "John Doe" in content
        assert "TechCorp" in content

    def test_truncate_context(self, engine):
        """Should truncate long text keeping head and tail."""
        long_text = "A" * 20000
        truncated = engine.truncate_context(long_text, max_chars=10000, preserve_tail=1000)
        assert len(truncated) < len(long_text)
        assert "[... content truncated ...]" in truncated

    def test_truncate_context_short(self, engine):
        """Should not truncate short text."""
        short_text = "Short text"
        truncated = engine.truncate_context(short_text, max_chars=10000)
        assert truncated == short_text

    def test_system_prompt_generation(self, engine):
        """Should generate system prompts for agents."""
        prompt = engine.render_system_prompt(
            "resume optimizer",
            ["ATS optimization", "Keyword extraction"],
        )
        assert "resume optimizer" in prompt
        assert "ATS optimization" in prompt
        assert "JSON" in prompt
