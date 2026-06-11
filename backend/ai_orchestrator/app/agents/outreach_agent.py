"""Outreach Agent - generates personalized cover letters and emails."""

from typing import Any, Optional

from ..schemas.agents import AgentCapability
from .base_agent import AgentResult, BaseAgent


class OutreachAgent(BaseAgent):
    """AI agent that generates personalized outreach content."""

    @property
    def agent_id(self) -> str:
        return "outreach"

    @property
    def name(self) -> str:
        return "Outreach Agent"

    @property
    def description(self) -> str:
        return "Generates personalized cover letters and outreach emails"

    @property
    def capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="cover_letter",
                description="Generate a personalized cover letter",
                required_inputs=["candidate_name", "company_name", "job_title", "skills"],
            ),
            AgentCapability(
                name="email_generation",
                description="Generate a personalized outreach email",
                required_inputs=["candidate_name", "company_name", "job_title"],
            ),
            AgentCapability(
                name="personalization",
                description="Extract personalization hooks from company data",
                required_inputs=["company_name", "job_title"],
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
        """Execute outreach based on capability requested."""
        capability = kwargs.get("capability", "cover_letter")

        template_map = {
            "cover_letter": "outreach/cover_letter.j2",
            "email_generation": "outreach/email_generation.j2",
            "personalization": "outreach/personalization.j2",
        }

        template = template_map.get(capability)
        if not template:
            return AgentResult(success=False, content="", error=f"Unknown capability: {capability}")

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
