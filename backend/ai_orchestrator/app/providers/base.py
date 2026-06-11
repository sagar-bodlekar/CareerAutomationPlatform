"""Abstract LLM provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


class ProviderError(Exception):
    """Raised when an LLM provider encounters an error."""

    def __init__(self, message: str, provider: str, recoverable: bool = True):
        self.message = message
        self.provider = provider
        self.recoverable = recoverable
        super().__init__(f"[{provider}] {message}")


@dataclass
class LLMResponse:
    """Structured response from an LLM provider."""

    content: str
    model_name: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0
    raw_response: Optional[dict] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier (e.g., 'gemini', 'groq')."""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model name for this provider."""
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a completion from the LLM.

        Args:
            prompt: The user/content prompt.
            system_prompt: Optional system instructions.
            model: Model override (uses default_model if None).
            temperature: Sampling temperature (0.0 - 1.0).
            max_tokens: Maximum tokens in response.

        Returns:
            LLMResponse with generated content and metadata.

        Raises:
            ProviderError: on API error, rate limit, or auth failure.
        """
        ...

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Generate a structured JSON response from the LLM.

        Uses lower temperature and requests JSON output format.
        """
        ...
