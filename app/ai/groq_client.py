# app/ai/groq_client.py
from groq import AsyncGroq

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.groq_api_key)
    return _client


async def groq_generate(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    """Generate text content using Groq Llama."""
    client = _get_client()
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content or ""
