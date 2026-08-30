import logging
import os

from dotenv import load_dotenv
from litellm import completion


logger = logging.getLogger(__name__)

load_dotenv()


GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DEFAULT_MAX_TOKENS = 4096


class LLMConfigurationError(ValueError):
    def __init__(self, message: str, *, original_exception: Exception | None = None):
        super().__init__(message)
        self.original_exception = original_exception


class PrimaryLLMFailure(RuntimeError):
    def __init__(self, message: str, *, primary_exception: Exception):
        super().__init__(message)
        self.primary_exception = primary_exception


class FallbackLLMFailure(PrimaryLLMFailure):
    def __init__(
        self,
        message: str,
        *,
        primary_exception: Exception,
        fallback_exception: Exception
    ):
        super().__init__(message, primary_exception=primary_exception)
        self.fallback_exception = fallback_exception


class RateLimitError(RuntimeError):
    def __init__(self, message: str, *, provider: str, original_exception: Exception):
        super().__init__(message)
        self.provider = provider
        self.original_exception = original_exception


def _is_rate_limit_error(error: Exception) -> bool:
    details = f"{type(error).__name__} {error}".lower()
    return (
        "rate limit" in details
        or "ratelimit" in details
        or "too many requests" in details
        or "429" in details
    )


def _completion_kwargs(
        model: str,
        api_key: str,
        messages: list,
        tools: list | None,
        tool_choice: str | dict | None,
        max_tokens: int | None = None,
) -> dict:

    kwargs = {
        "model": model,
        "api_key": api_key,
        "messages": messages
    }

    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    if tools:
        kwargs["tools"] = tools

        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

    return kwargs


def completion_with_fallback(
        messages: list,
        tools: list | None = None,
        tool_choice: str | dict | None = None,
        max_tokens: int | None = DEFAULT_MAX_TOKENS
):

    if not GROQ_MODEL:
        raise LLMConfigurationError("GROQ_MODEL is not set in .env")

    if not GROQ_API_KEY:
        raise LLMConfigurationError("GROQ_API_KEY is not set in .env")

    if tools is not None and tool_choice is None:
        tool_choice = "auto"

    kwargs = _completion_kwargs(
        model=f"groq/{GROQ_MODEL}",
        api_key=GROQ_API_KEY,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        max_tokens=max_tokens,
    )

    try:
        return completion(**kwargs)
    except Exception as primary_error:
        logger.exception("Primary Groq LLM request failed.")

        if not GEMINI_MODEL or not GEMINI_API_KEY:
            raise PrimaryLLMFailure(
                "Primary Groq LLM failed and Gemini fallback is not configured.",
                primary_exception=primary_error,
            ) from primary_error

        fallback_kwargs = _completion_kwargs(
            model=GEMINI_MODEL,
            api_key=GEMINI_API_KEY,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            max_tokens=max_tokens,
        )

        try:
            return completion(**fallback_kwargs)
        except Exception as fallback_error:
            logger.exception("Gemini fallback LLM request failed.")

            if _is_rate_limit_error(primary_error) or _is_rate_limit_error(fallback_error):
                raise RateLimitError(
                    "Groq primary and/or Gemini fallback hit a rate limit.",
                    provider="Gemini" if _is_rate_limit_error(fallback_error) else "Groq",
                    original_exception=fallback_error if _is_rate_limit_error(fallback_error) else primary_error,
                ) from fallback_error if _is_rate_limit_error(fallback_error) else primary_error

            raise FallbackLLMFailure(
                "Primary Groq LLM failed and Gemini fallback also failed.",
                primary_exception=primary_error,
                fallback_exception=fallback_error,
            ) from fallback_error


def ask_llm(
        system_prompt: str,
        user_prompt: str
) -> str:

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = completion_with_fallback(
        messages=messages
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError(
            "LLM returned no content."
        )

    return content


if __name__ == "__main__":

    response = ask_llm(
        system_prompt=(
            "You are a helpful business analyst."
        ),
        user_prompt=(
            "Explain what ROAS means in one sentence."
        )
    )

    print(response)