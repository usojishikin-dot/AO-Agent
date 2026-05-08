# app/ai/gemini_client.py
import asyncio

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: genai.Client | None = None

# Retry settings for 429 / RESOURCE_EXHAUSTED
_MAX_RETRIES = 3
_BASE_DELAY = 10  # seconds


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _is_retryable_error(exc: Exception) -> bool:
    """Return True for transient Gemini errors that warrant a retry.

    Covers:
      - 429 RESOURCE_EXHAUSTED — rate limit
      - 503 UNAVAILABLE       — model overload / temporary outage
    """
    msg = str(exc)
    return (
        "429" in msg or "RESOURCE_EXHAUSTED" in msg
        or "503" in msg or "UNAVAILABLE" in msg
    )


async def _retry_generate(coro_factory, *, label: str):
    """Run coro_factory(), retrying up to _MAX_RETRIES times on transient errors."""
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return await coro_factory()
        except Exception as exc:
            if _is_retryable_error(exc) and attempt < _MAX_RETRIES:
                delay = _BASE_DELAY * (2 ** (attempt - 1))  # 10s, 20s, 40s
                logger.warning(
                    "Gemini transient error — backing off",
                    extra={
                        "label": label,
                        "attempt": attempt,
                        "retry_in_seconds": delay,
                        "error": str(exc)[:120],
                    },
                )
                await asyncio.sleep(delay)
            else:
                raise


async def gemini_generate_json(prompt: str, model: str) -> str:
    """Call Gemini and return a raw JSON string, with 429 backoff retry."""
    client = _get_client()

    async def _call():
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return response.text

    return await _retry_generate(_call, label=f"gemini_json:{model}")


async def gemini_generate_text(prompt: str, model: str) -> str:
    """Call Gemini and return plain text, with 429 backoff retry."""
    client = _get_client()

    async def _call():
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text

    return await _retry_generate(_call, label=f"gemini_text:{model}")
