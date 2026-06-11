"""Prompt template engine using Jinja2."""

import os
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class PromptEngine:
    """Loads and renders Jinja2 prompt templates from the prompts directory.

    Templates are stored in app/prompts/ organized by agent.
    """

    def __init__(self, template_dir: Optional[str] = None):
        self._template_dir = template_dir or self._default_template_dir()
        self._env = Environment(
            loader=FileSystemLoader(self._template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _default_template_dir(self) -> str:
        """Find the prompts directory relative to this file."""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

    def list_templates(self) -> list[str]:
        """List all available prompt templates."""
        templates = []
        base = Path(self._template_dir)
        if not base.exists():
            return templates
        for path in base.rglob("*.j2"):
            rel = path.relative_to(base)
            templates.append(str(rel).replace("\\", "/"))
        return sorted(templates)

    def render(self, template_name: str, variables: dict[str, Any]) -> str:
        """Render a prompt template with variables.

        Args:
            template_name: Path relative to prompts dir (e.g., 'resume_optimizer/ats_optimization.j2')
            variables: Dict of variables to inject into template.

        Returns:
            Rendered prompt string.

        Raises:
            TemplateNotFound: if template doesn't exist.
        """
        try:
            template = self._env.get_template(template_name)
        except TemplateNotFound:
            # Try with .j2 extension if not provided
            if not template_name.endswith(".j2"):
                template_name = f"{template_name}.j2"
            template = self._env.get_template(template_name)

        return template.render(**variables)

    def render_system_prompt(self, agent_name: str, capabilities: list[str]) -> str:
        """Generate a system prompt for an agent.

        Args:
            agent_name: Name of the agent.
            capabilities: List of capabilities to include.

        Returns:
            System prompt string.
        """
        capabilities_str = "\n".join(f"- {c}" for c in capabilities)
        return f"""You are an AI {agent_name} agent for a career automation platform. Your role is to help users optimize their job applications.

Capabilities:
{capabilities_str}

Follow these rules:
1. Always respond with valid JSON when structured output is requested.
2. Be specific, actionable, and professional.
3. Base your analysis only on the data provided in the prompt.
4. If information is missing, note it rather than making assumptions.
5. Keep responses concise and focused on the task."""

    def truncate_context(
        self,
        text: str,
        max_chars: int = 15000,
        preserve_tail: int = 2000,
    ) -> str:
        """Truncate context text to fit within token limits.

        Keeps the beginning (most important) and end (most recent) of the text.

        Args:
            text: Text to truncate.
            max_chars: Maximum character length.
            preserve_tail: Number of characters to preserve from the end.

        Returns:
            Truncated text.
        """
        if len(text) <= max_chars:
            return text

        head_len = max_chars - preserve_tail - 100  # 100 for truncation notice
        head = text[:head_len]
        tail = text[-preserve_tail:]
        return f"{head}\n\n[... content truncated ...]\n\n{tail}"
