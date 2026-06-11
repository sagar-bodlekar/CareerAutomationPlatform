"""Resume Optimizer Agent - optimizes resumes for ATS and specific roles."""

from typing import Any, Optional

from ..schemas.agents import AgentCapability
from .base_agent import AgentResult, BaseAgent


class ResumeOptimizerAgent(BaseAgent):
    """AI agent that optimizes resumes for ATS compatibility and role matching."""

    @property
    def agent_id(self) -> str:
        return "resume_optimizer"

    @property
    def name(self) -> str:
        return "Resume Optimizer"

    @property
    def description(self) -> str:
        return "Optimizes resumes for ATS compatibility and specific job roles"

    @property
    def capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="ats_optimization",
                description="Analyze resume against job description for ATS optimization",
                required_inputs=["resume_content", "job_description"],
            ),
            AgentCapability(
                name="keyword_extraction",
                description="Extract key skills and requirements from job descriptions",
                required_inputs=["job_description"],
            ),
            AgentCapability(
                name="resume_scoring",
                description="Score resume compatibility with a target job",
                required_inputs=["resume_content", "job_title", "job_description"],
            ),
            AgentCapability(
                name="resume_tailoring",
                description="Tailor resume content for a specific job application",
                required_inputs=["resume_sections", "job_description", "target_role"],
            ),
        ]

    @property
    def default_model(self) -> str:
        return "gemini-2.0-flash"

    async def execute(
        self,
        inputs: dict[str, Any],
        **kwargs,
    ) -> AgentResult:
        """Execute resume optimization based on capability requested."""
        capability = kwargs.get("capability", "ats_optimization")

        # Map capability to prompt template
        template_map = {
            "ats_optimization": "resume_optimizer/ats_optimization.j2",
            "keyword_extraction": "resume_optimizer/keyword_extraction.j2",
            "resume_scoring": "resume_optimizer/resume_scoring.j2",
            "resume_tailoring": "resume_optimizer/resume_tailoring.j2",
        }

        template = template_map.get(capability)
        if not template:
            return AgentResult(
                success=False,
                content="",
                error=f"Unknown capability: {capability}",
            )

        response = await self.execute_with_orchestrator(
            inputs=inputs,
            prompt_template=template,
            use_structured=True,
        )

        return AgentResult(
            success=response.success,
            content=response.content,
            structured_data=response.structured,
            error=response.error,
            execution_time_ms=response.duration_ms,
            tokens_used=response.total_tokens,
        )
