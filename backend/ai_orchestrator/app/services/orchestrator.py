"""AI Orchestrator - coordinates LLM providers, prompts, and response parsing."""

import json
import logging
import time
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings as app_settings

from ..models.models import AIExecutionLog
from ..providers import GeminiProvider, GroqProvider, LLMProvider, ProviderError
from ..schemas.agents import ExecuteRequest, ExecuteResponse
from .prompt_engine import PromptEngine
from .response_parser import ResponseParser

logger = logging.getLogger(__name__)


# Cost per 1K tokens (approximate USD)
MODEL_COST_MAP: dict[str, dict[str, float]] = {
    "gemini-2.0-flash": {"input": 0.00010, "output": 0.00040},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.00500},
    "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
    "mixtral-8x7b-32768": {"input": 0.00024, "output": 0.00024},
}


class AIOrchestrator:
    """Central orchestrator for AI-powered operations.

    Coordinates:
    1. Provider selection and fallback (Gemini -> Groq)
    2. Prompt template rendering
    3. LLM execution with retry
    4. Response parsing and validation
    5. Execution logging
    """

    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        prompt_engine: Optional[PromptEngine] = None,
        response_parser: Optional[ResponseParser] = None,
    ):
        self.db = db
        self.prompt_engine = prompt_engine or PromptEngine()
        self.response_parser = response_parser or ResponseParser()
        self._providers: list[LLMProvider] = []

    def _get_providers(self) -> list[LLMProvider]:
        """Get configured providers in priority order."""
        if not self._providers:
            providers = []
            if app_settings.gemini_api_key:
                providers.append(GeminiProvider())
            if app_settings.groq_api_key:
                providers.append(GroqProvider())

            if not providers:
                logger.warning(
                    "No LLM providers configured. Set GEMINI_API_KEY or GROQ_API_KEY."
                )
            self._providers = providers
        return self._providers

    def _estimate_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for a model call."""
        # Check known models
        for model_key, rates in MODEL_COST_MAP.items():
            if model_key in model_name:
                input_cost = (input_tokens / 1000) * rates["input"]
                output_cost = (output_tokens / 1000) * rates["output"]
                return round(input_cost + output_cost, 6)

        # Default estimate if unknown model
        return round((input_tokens + output_tokens) / 1000 * 0.0002, 6)

    async def execute(
        self,
        request: ExecuteRequest,
        system_prompt: Optional[str] = None,
        prompt_template: Optional[str] = None,
    ) -> ExecuteResponse:
        """Execute an AI task through the provider chain.

        Args:
            request: Execution request with agent_id, inputs, etc.
            system_prompt: Optional system prompt override.
            prompt_template: Optional specific template path override.
                If not provided, defaults to '{agent_id}/prompt.j2'.

        Returns:
            ExecuteResponse with content, metadata, and execution log.
        """
        providers = self._get_providers()
        if not providers:
            return ExecuteResponse(
                success=False,
                agent_id=request.agent_id,
                content="",
                model_used="",
                provider_used="",
                error="No AI providers configured. Set GEMINI_API_KEY or GROQ_API_KEY.",
            )

        start_time = time.time()
        fallback_used = False
        last_error = None

        # Render prompt
        prompt_text = request.prompt or ""
        if not prompt_text and request.inputs:
            template_path = prompt_template or f"{request.agent_id}/prompt.j2"
            try:
                prompt_text = self.prompt_engine.render(
                    template_path,
                    request.inputs,
                )
            except Exception:
                prompt_text = json.dumps(request.inputs, indent=2)

        # Try providers in order (Gemini -> Groq)
        for i, provider in enumerate(providers):
            try:
                if request.use_structured_output:
                    response = await provider.generate_structured(
                        prompt=prompt_text,
                        system_prompt=system_prompt,
                        model=request.model,
                        temperature=request.temperature,
                    )
                else:
                    response = await provider.generate(
                        prompt=prompt_text,
                        system_prompt=system_prompt,
                        model=request.model,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                    )

                fallback_used = i > 0
                duration_ms = int((time.time() - start_time) * 1000)

                # Parse structured output
                structured_data = None
                if request.use_structured_output and response.content:
                    try:
                        structured_data, _ = self.response_parser.parse_with_retry(
                            response.content
                        )
                    except ValueError as e:
                        logger.warning(f"Structured parse failed: {e}")

                # Log execution
                execution_id = await self._log_execution(
                    agent_name=request.agent_id,
                    model_provider=response.provider,
                    model_name=response.model_name,
                    prompt_template=f"{request.agent_id}/prompt.j2",
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    total_tokens=response.total_tokens,
                    duration_ms=duration_ms,
                    success=True,
                    retry_count=0,
                    provider_fallback_used=fallback_used,
                    input_preview=prompt_text[:200],
                    output_preview=response.content[:200],
                    user_id=request.user_id,
                    profile_id=request.profile_id,
                    job_id=request.job_id,
                )

                return ExecuteResponse(
                    success=True,
                    agent_id=request.agent_id,
                    content=response.content,
                    structured=structured_data,
                    model_used=response.model_name,
                    provider_used=response.provider,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    total_tokens=response.total_tokens,
                    duration_ms=duration_ms,
                    fallback_used=fallback_used,
                    execution_id=execution_id,
                )

            except ProviderError as e:
                last_error = str(e)
                logger.warning(f"Provider {provider.provider_name} failed: {e}")
                if not e.recoverable:
                    # Non-recoverable error, don't try fallback
                    break
                continue

            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error with {provider.provider_name}: {e}")
                continue

        # All providers failed
        duration_ms = int((time.time() - start_time) * 1000)
        await self._log_execution(
            agent_name=request.agent_id,
            model_provider=providers[-1].provider_name if providers else "none",
            model_name=request.model or "unknown",
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            duration_ms=duration_ms,
            success=False,
            error_message=last_error or "All providers failed",
            input_preview=prompt_text[:200],
            user_id=request.user_id,
            profile_id=request.profile_id,
            job_id=request.job_id,
        )

        return ExecuteResponse(
            success=False,
            agent_id=request.agent_id,
            content="",
            model_used=request.model or "unknown",
            provider_used=providers[-1].provider_name if providers else "none",
            error=last_error or "All providers failed",
            duration_ms=duration_ms,
        )

    async def _log_execution(
        self,
        agent_name: str,
        model_provider: str,
        model_name: str,
        prompt_template: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        duration_ms: int = 0,
        success: bool = True,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        provider_fallback_used: bool = False,
        input_preview: Optional[str] = None,
        output_preview: Optional[str] = None,
        user_id: Optional[int] = None,
        profile_id: Optional[int] = None,
        job_id: Optional[int] = None,
    ) -> Optional[int]:
        """Log an AI execution to the database."""
        if not self.db:
            return None

        try:
            log_entry = AIExecutionLog(
                agent_name=agent_name,
                model_provider=model_provider,
                model_name=model_name,
                prompt_template=prompt_template,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_estimate=self._estimate_cost(model_name, input_tokens, output_tokens),
                duration_ms=duration_ms,
                success=1 if success else 0,
                error_message=error_message,
                retry_count=retry_count,
                provider_fallback_used=1 if provider_fallback_used else 0,
                input_preview=input_preview,
                output_preview=output_preview,
                user_id=user_id,
                profile_id=profile_id,
                job_id=job_id,
            )
            self.db.add(log_entry)
            await self.db.flush()
            return log_entry.id
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
            return None

    async def get_usage_stats(
        self,
        db: AsyncSession,
        agent_name: Optional[str] = None,
        since_hours: int = 24,
    ) -> dict[str, Any]:
        """Get usage statistics for AI executions."""
        query = select(AIExecutionLog)
        if agent_name:
            query = query.where(AIExecutionLog.agent_name == agent_name)

        result = await db.execute(query)
        logs = result.scalars().all()

        total_input = sum(l.input_tokens or 0 for l in logs)
        total_output = sum(l.output_tokens or 0 for l in logs)
        total_executions = len(logs)
        successful = sum(1 for l in logs if l.success)

        return {
            "total_executions": total_executions,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "success_rate": round(successful / total_executions * 100, 1) if total_executions else 0,
            "estimated_cost_usd": round(
                sum(self._estimate_cost(l.model_name, l.input_tokens or 0, l.output_tokens or 0) for l in logs), 4
            ),
        }
