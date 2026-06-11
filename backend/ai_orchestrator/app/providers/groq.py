"""Groq LLM provider (OpenAI-compatible API)."""

import time
from typing import Optional

from shared.config import settings

from .base import LLMProvider, LLMResponse, ProviderError


class GroqProvider(LLMProvider):
    """LLM provider for Groq API (OpenAI-compatible).

    Falls back to this provider when Gemini is unavailable.
    Uses the openai SDK pointed at api.groq.com.
    """

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def default_model(self) -> str:
        return self.config.get("model", settings.groq_default_model)

    def _get_client(self):
        """Lazy-import and create the OpenAI-compatible client."""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                api_key=settings.groq_api_key_required,
                base_url=settings.groq_base_url,
            )
            return client
        except ImportError:
            raise ProviderError(
                "openai package not installed. Run: pip install openai",
                self.provider_name,
                recoverable=False,
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to create Groq client: {e}",
                self.provider_name,
                recoverable=False,
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate content using Groq API."""
        model_name = model or self.default_model
        client = self._get_client()
        start_time = time.time()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 8192,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice else ""

            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            return LLMResponse(
                content=content,
                model_name=model_name,
                provider=self.provider_name,
                input_tokens=input_tokens or 0,
                output_tokens=output_tokens or 0,
                total_tokens=total_tokens or 0,
                duration_ms=duration_ms,
                raw_response={
                    "finish_reason": choice.finish_reason if choice else None,
                },
            )

        except Exception as e:
            error_str = str(e)
            recoverable = True
            if "API_KEY" in error_str.upper() or "AUTH" in error_str.upper():
                recoverable = False
            if "RATE_LIMIT" in error_str.upper() or "429" in error_str:
                recoverable = True

            raise ProviderError(
                f"Groq API error: {error_str[:300]}",
                self.provider_name,
                recoverable=recoverable,
            )

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Generate structured JSON response using Groq.

        Uses response_format to request JSON output.
        """
        model_name = model or self.default_model
        client = self._get_client()
        start_time = time.time()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=8192,
                response_format={"type": "json_object"},
            )

            duration_ms = int((time.time() - start_time) * 1000)

            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice else ""

            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            return LLMResponse(
                content=content,
                model_name=model_name,
                provider=self.provider_name,
                input_tokens=input_tokens or 0,
                output_tokens=output_tokens or 0,
                total_tokens=total_tokens or 0,
                duration_ms=duration_ms,
            )

        except Exception as e:
            raise ProviderError(
                f"Groq structured error: {str(e)[:300]}",
                self.provider_name,
            )
