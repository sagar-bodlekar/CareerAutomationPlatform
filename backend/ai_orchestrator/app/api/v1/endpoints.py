"""AI Orchestrator API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_session
from shared.schemas.common import APIResponse

from ...agents import AGENT_REGISTRY
from ...agents.base_agent import BaseAgent
from ...schemas.agents import AgentDefinition, ExecuteRequest, ExecuteResponse
from ...services.orchestrator import AIOrchestrator
from .dependencies import get_current_user_id, get_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Orchestrator"])


def _get_agent(orchestrator: AIOrchestrator, agent_id: str) -> BaseAgent:
    """Get an agent instance by ID, creating it with the orchestrator."""
    agent_cls = AGENT_REGISTRY.get(agent_id)
    if not agent_cls:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent: {agent_id}. Available: {', '.join(AGENT_REGISTRY.keys())}",
        )
    return agent_cls(orchestrator=orchestrator)


@router.post("/execute", response_model=APIResponse[ExecuteResponse])
async def execute_ai(
    request: ExecuteRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Execute an AI task by agent name.

    The agent processes the inputs and returns structured results.
    Supports resume optimization, job matching, outreach, and career intelligence.
    """
    agent = _get_agent(orchestrator, request.agent_id)

    # Execute using the agent
    result = await agent.execute(
        inputs=request.inputs,
        capability=request.inputs.get("capability", ""),
    )

    return APIResponse(data=ExecuteResponse(
        success=result.success,
        agent_id=agent.agent_id,
        content=result.content,
        structured=result.structured_data,
        model_used=agent.default_model,
        provider_used="gemini",
        duration_ms=result.execution_time_ms,
        total_tokens=result.tokens_used,
        error=result.error,
    ))


@router.get("/agents", response_model=APIResponse[list[AgentDefinition]])
async def list_agents(
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """List all configured AI agents and their capabilities."""
    agents = []
    for agent_id, agent_cls in AGENT_REGISTRY.items():
        agent = agent_cls(orchestrator=orchestrator)
        agents.append(agent.get_definition())
    return APIResponse(data=agents)


@router.get("/agents/{agent_id}", response_model=APIResponse[AgentDefinition])
async def get_agent_details(
    agent_id: str,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get details about a specific AI agent."""
    agent = _get_agent(orchestrator, agent_id)
    return APIResponse(data=agent.get_definition())


@router.get("/usage", response_model=APIResponse)
async def get_usage_stats(
    agent_name: Optional[str] = Query(None),
    since_hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_session),
    _user_id: Optional[int] = Depends(get_current_user_id),
):
    """Get AI usage statistics (token usage, cost estimates)."""
    orchestrator = AIOrchestrator(db=db)
    stats = await orchestrator.get_usage_stats(
        db=db,
        agent_name=agent_name,
        since_hours=since_hours,
    )
    return APIResponse(data=stats)
