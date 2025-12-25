"""LLM provider factory."""

import logging
import os
import re
from typing import Any

from browser_use import ChatAnthropic, ChatOpenAI
from browser_use.llm.messages import BaseMessage
from browser_use.llm.openrouter.chat import ChatOpenRouter
from browser_use.llm.openrouter.serializer import OpenRouterMessageSerializer
from browser_use.llm.schema import SchemaOptimizer
from browser_use.llm.views import ChatInvokeCompletion
from openai import AsyncOpenAI
from openai.types.shared_params.response_format_json_schema import (
    ResponseFormatJSONSchema,
)

from engagerunner.models import LLMConfig

logger = logging.getLogger(__name__)


class MarkdownStrippingChatOpenRouter(ChatOpenRouter):
    """ChatOpenRouter that strips markdown code blocks from structured output.

    Many free models (like Gemini) wrap JSON in markdown blocks which breaks
    Pydantic validation. This wrapper strips the markdown before parsing.
    """

    async def ainvoke(
        self,
        messages: list[BaseMessage],
        output_format: type | None = None,
        **kwargs: Any,
    ) -> Any:
        """Invoke LLM and strip markdown from structured output before validation."""
        # Call parent implementation but catch the response before validation
        try:
            return await super().ainvoke(messages, output_format, **kwargs)
        except Exception as e:
            # If it's a JSON validation error, try stripping markdown
            if "Invalid JSON" in str(e) and output_format is not None:
                logger.debug("JSON validation failed, attempting markdown strip: %s", e)

                # Get the raw response by calling OpenAI client directly
                openrouter_messages = OpenRouterMessageSerializer.serialize_messages(messages)

                # Create client with same settings
                client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url or "https://openrouter.ai/api/v1",
                )

                schema = SchemaOptimizer.create_optimized_json_schema(output_format)
                response_format_schema = {
                    "name": "agent_output",
                    "strict": True,
                    "schema": schema,
                }

                response = await client.chat.completions.create(
                    model=self.model,
                    messages=openrouter_messages,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    seed=self.seed,
                    response_format=ResponseFormatJSONSchema(
                        json_schema=response_format_schema,  # type: ignore[typeddict-item]
                        type="json_schema",
                    ),
                    extra_headers={"HTTP-Referer": "https://engagerunner.com"},
                )

                if response.choices[0].message.content is None:
                    raise

                # Strip markdown code blocks
                content = response.choices[0].message.content
                stripped = self._strip_markdown(content)

                # Try parsing with stripped content
                try:
                    parsed = output_format.model_validate_json(stripped)  # type: ignore[attr-defined]
                    usage = self._get_usage(response)
                    logger.info("Successfully parsed JSON after markdown stripping")
                    return ChatInvokeCompletion(completion=parsed, usage=usage)
                except Exception:
                    logger.exception("Failed to parse even after stripping")
                    raise

            # Re-raise if not a fixable JSON error
            raise

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Strip markdown code blocks from text.

        Args:
            text: Text potentially wrapped in ```json ... ```

        Returns:
            Stripped text with just the JSON content
        """
        # Remove ```json and ``` markers
        text = re.sub(r"^```(?:json)?\s*\n", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n```\s*$", "", text, flags=re.MULTILINE)
        return text.strip()


class RetryLLM:
    """LLM wrapper with automatic retry and fallback to alternative models."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize retry LLM wrapper.

        Args:
            config: LLM configuration
        """
        self.config = config
        self.models_to_try = [config.model, *config.fallback_models]
        self.current_model_index = 0
        self.llm = self._create_llm_instance(self.models_to_try[0])

    def _create_llm_instance(self, model: str) -> Any:
        """Create LLM instance for a specific model.

        Args:
            model: Model identifier

        Returns:
            Browser-use compatible chat model instance

        Raises:
            ValueError: If provider is unsupported
        """
        if not self.config.api_key:
            msg = "API key is required for LLM provider"
            raise ValueError(msg)

        logger.info("Creating LLM instance with model: %s", model)

        if self.config.provider == "openrouter":
            return MarkdownStrippingChatOpenRouter(model=model, api_key=self.config.api_key)
        if self.config.provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = self.config.api_key
            return ChatAnthropic(model=model)
        if self.config.provider == "openai":
            os.environ["OPENAI_API_KEY"] = self.config.api_key
            return ChatOpenAI(model=model)
        msg = f"Unsupported LLM provider: {self.config.provider}"
        raise ValueError(msg)

    def try_next_model(self) -> bool:
        """Switch to the next available model.

        Returns:
            True if switched to next model, False if no more models available
        """
        self.current_model_index += 1
        if self.current_model_index >= len(self.models_to_try):
            logger.error("No more models to try")
            return False

        next_model = self.models_to_try[self.current_model_index]
        logger.warning("Switching to fallback model: %s", next_model)
        try:
            self.llm = self._create_llm_instance(next_model)
        except Exception:
            logger.exception("Failed to create LLM instance for model: %s", next_model)
            return self.try_next_model()
        else:
            return True

    def __getattr__(self, name: str) -> Any:
        """Delegate all attribute access to the underlying LLM instance."""
        return getattr(self.llm, name)


def create_llm(config: LLMConfig) -> RetryLLM:
    """Create LLM instance with retry and fallback support.

    Args:
        config: LLM configuration

    Returns:
        RetryLLM wrapper instance
    """
    return RetryLLM(config)
