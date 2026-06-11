"""Google Gemini LLM provider."""

import time
from typing import Optional

from shared.config import settings

from .base import LLMProvider, LLMResponse, ProviderError


class GeminiProvider(LLMProvider):
    """LLM provider for Google Gemini API.

    Uses the google-genai SDK for async generation.
    """

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return self.config.get("model", settings.gemini_default_model)

    def _get_client(self):
        """Lazy-import and create the Gemini client."""
        try:
            from google import genai
            client = genai.Client(api_key=settings.gemini_api_key_required)
            return client
        except ImportError:
            raise ProviderError(
                "google-genai package not installed. Run: pip install google-genai",
                self.provider_name,
                recoverable=False,
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to create Gemini client: {e}",
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
        """Generate content using Gemini API."""
        model_name = model or self.default_model
        client = self._get_client()
        start_time = time.time()

        try:
            # Build contents
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [{"text": system_prompt}]})
                contents.append({"role": "model", "parts": [{"text": "Understood."}]})
            contents.append({"role": "user", "parts": [{"text": prompt}]})

            gen_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens or 8192,
            }

            response = await client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=gen_config,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Extract text from response
            content = response.text if hasattr(response, "text") else ""

            # Token counts
            usage = getattr(response, "usage_metadata", None)
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            total_tokens = usage.total_token_count if usage else 0

            return LLMResponse(
                content=content,
                model_name=model_name,
                provider=self.provider_name,
                input_tokens=input_tokens or 0,
                output_tokens=output_tokens or 0,
                total_tokens=total_tokens or 0,
                duration_ms=duration_ms,
                raw_response={"finish_reason": getattr(response, "finish_reason", None)},
            )

        except Exception as e:
            error_str = str(e)
            # Determine if error is recoverable
            recoverable = True
            if "API_KEY" in error_str.upper() or "PERMISSION" in error_str.upper():
                recoverable = False
            if "RATE_LIMIT" in error_str.upper() or "QUOTA" in error_str.upper():
                recoverable = True

            raise ProviderError(
                f"Gemini API error: {error_str[:300]}",
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
        """Generate structured JSON response using Gemini.

        Sets response_mime_type to application/json when available.
        """
        model_name = model or self.default_model
        client = self._get_client()
        start_time = time.time()

        try:
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [{"text": system_prompt}]})
                contents.append({"role": "model", "parts": [{"text": "Understood."}]})
            contents.append({"role": "user", "parts": [{"text": prompt}]})

            gen_config = {
                "temperature": temperature,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }

            response = await client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=gen_config,
            )

            duration_ms = int((time.time() - start_time) * 1000)
            content = response.text if hasattr(response, "text") else ""

            usage = getattr(response, "usage_metadata", None)
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            total_tokens = usage.total_token_count if usage else 0

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
                f"Gemini structured error: {str(e)[:300]}",
                self.provider_name,
            )
