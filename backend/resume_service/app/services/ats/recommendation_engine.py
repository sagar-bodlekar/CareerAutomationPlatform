"""ATS Recommendation Engine — generates actionable suggestions to improve ATS score."""

class ATSRecommendationEngine:
    """Generates human-readable recommendations to improve ATS compatibility."""

    def generate_recommendations(
        self,
        score_breakdown: dict,
        resume_content: dict,
        job_description: str,
    ) -> list[str]:
        """Generate recommendations based on score breakdown.

        Args:
            score_breakdown: The score dict from ATSScorer.
            resume_content: The resume content dict.
            job_description: The target job description.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        # Keyword recommendations
        missing_keywords = score_breakdown.get("missing_keywords", [])
        if missing_keywords:
            if len(missing_keywords) <= 5:
                recommendations.append(
                    f"Add missing keywords to your resume: {', '.join(missing_keywords[:5])}."
                )
            else:
                recommendations.append(
                    f"You're missing {len(missing_keywords)} key terms. "
                    f"Prioritize adding: {', '.join(missing_keywords[:5])}."
                )

        # Section recommendations
        section_score = score_breakdown.get("section_score", 100)
        if section_score < 100:
            missing_sections = self._find_missing_sections(resume_content)
            if missing_sections:
                recommendations.append(
                    f"Add the '{missing_sections[0]}' section to your resume."
                )
            recommendations.append(
                "Ensure your resume includes all standard sections: "
                "Summary, Experience, Education, and Skills."
            )

        # Experience recommendations
        exp_score = score_breakdown.get("experience_score", 100)
        if exp_score < 60:
            recommendations.append(
                "Your experience duration may be below the job requirement. "
                "Emphasize relevant projects and achievements to compensate."
            )
        elif exp_score < 80:
            recommendations.append(
                "Highlight your most relevant experience prominently. "
                "Consider reordering sections to feature matching roles first."
            )

        # Skills recommendations
        skills_score = score_breakdown.get("skills_score", 100)
        if skills_score < 40:
            recommendations.append(
                "Your skills section has low alignment with this role. "
                "Consider adding missing technical skills and highlighting "
                "transferable expertise."
            )

        # General recommendations
        keyword_score = score_breakdown.get("keyword_score", 100)
        if keyword_score < 30:
            recommendations.append(
                "Your resume lacks keywords from the job description. "
                "Incorporate relevant terms naturally into your "
                "experience descriptions and summary."
            )

        recommendations.append(
            "Use bullet points with quantified achievements "
            "(e.g., 'Improved performance by 40%') for maximum impact."
        )

        return recommendations

    def _find_missing_sections(self, content: dict) -> list[str]:
        """Find standard resume sections that are missing."""
        required = ["summary", "experiences", "education", "skills", "projects"]
        missing = []
        for section in required:
            if section == "experiences":
                if not content.get("experiences"):
                    missing.append("experience")
            elif not content.get(section):
                missing.append(section)
        return missing
