"""AI Orchestrator dependencies."""

from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session

from ...agents import AGENT_REGISTRY, BaseAgent
from ...services.orchestrator import AIOrchestrator
from ...services.prompt_engine import PromptEngine
from ...services.response_parser import ResponseParser


async def get_orchestrator(
    db: AsyncSession = Depends(get_session),
) -> AIOrchestrator:
    return AIOrchestrator(
        db=db,
        prompt_engine=PromptEngine(),
        response_parser=ResponseParser(),
    )


async def get_agent(agent_id: str) -> Optional[BaseAgent]:
    """Get an agent instance by ID."""
    agent_cls = AGENT_REGISTRY.get(agent_id)
    if not agent_cls:
        return None
    return None  # Agent needs orchestrator, injected in endpoint


async def get_current_user_id(request: Request) -> Optional[int]:
    return None
