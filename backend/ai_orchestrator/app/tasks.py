"""Celery tasks for AI orchestrator."""

import asyncio
import logging

from celery import Celery

from shared.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "ai_orchestrator",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def ai_execute(self, agent_id: str, inputs: dict, capability: str = ""):
    """Execute an AI task asynchronously."""
    try:
        from .agents import AGENT_REGISTRY
        from .services.orchestrator import AIOrchestrator
        from .services.prompt_engine import PromptEngine
        from .services.response_parser import ResponseParser
        from shared.database import async_session_factory

        async def _execute():
            async with async_session_factory() as session:
                orchestrator = AIOrchestrator(
                    db=session,
                    prompt_engine=PromptEngine(),
                    response_parser=ResponseParser(),
                )
                agent_cls = AGENT_REGISTRY.get(agent_id)
                if not agent_cls:
                    return {"error": f"Unknown agent: {agent_id}"}
                agent = agent_cls(orchestrator=orchestrator)
                result = await agent.execute(inputs=inputs, capability=capability)
                return {
                    "success": result.success,
                    "content_preview": result.content[:200] if result.content else "",
                    "structured": result.structured_data,
                    "error": result.error,
                }

        return asyncio.run(_execute())
    except Exception as exc:
        logger.error(f"AI execute task failed for {agent_id}: {exc}")
        raise self.retry(exc=exc)
