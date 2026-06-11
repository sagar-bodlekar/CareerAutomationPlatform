"""Tests for ContentAssembler."""

from app.services.content_assembler import ContentAssembler


class TestContentAssembler:
    """Test that profile data is correctly assembled into resume content."""

    def setup_method(self):
        self.assembler = ContentAssembler()

    def test_from_profile_with_full_data(self):
        profile = {
            "headline": "Senior Developer",
            "summary": "Experienced developer.",
            "personal_info": {
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+1-555-0100",
                "city": "Portland",
                "country": "USA",
            },
            "skills": [
                {"name": "Python", "category": "Language", "proficiency": "expert"},
                {"name": "React", "category": "Framework", "proficiency": "advanced"},
            ],
            "work_experiences": [
                {
                    "company_name": "Acme Corp",
                    "job_title": "Senior Engineer",
                    "start_date": "2020-01-01",
                    "is_current": True,
                    "description": "Building great things.",
                }
            ],
            "education": [
                {
                    "institution": "MIT",
                    "degree": "B.S. Computer Science",
                    "start_date": "2012-09-01",
                    "end_date": "2016-06-01",
                }
            ],
            "projects": [
                {"name": "Career Platform", "description": "AI platform", "technologies": ["Python"]}
            ],
            "certifications": [
                {"name": "AWS Certified", "issuer": "Amazon", "issue_date": "2023-01-15"}
            ],
            "social_links": [
                {"platform": "github", "url": "https://github.com/janedoe"}
            ],
        }

        content = self.assembler.from_profile(profile)
        assert content["name"] == "Jane Doe"
        assert content["title"] == "Senior Developer"
        assert content["summary"] == "Experienced developer."
        assert len(content["contact"]) >= 3  # email, phone, github
        assert "Language" in content["skills"]
        assert len(content["experiences"]) == 1
        assert content["experiences"][0]["company_name"] == "Acme Corp"
        assert len(content["education"]) == 1
        assert len(content["projects"]) == 1
        assert len(content["certifications"]) == 1

    def test_from_profile_minimal(self):
        profile = {
            "headline": "",
            "summary": "",
            "personal_info": None,
            "skills": [],
            "work_experiences": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "social_links": [],
        }
        content = self.assembler.from_profile(profile)
        assert content["name"] == ""
        assert content["flat_skills"] == []
        assert content["experiences"] == []
