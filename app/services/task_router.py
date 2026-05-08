# app/services/task_router.py
import json

from pydantic import BaseModel

from app.ai.gemini_client import gemini_generate_json
from app.core.logging import get_logger
from app.services.prompt_processor import ProcessedContent

logger = get_logger(__name__)

GEMINI_FLASH_MODEL = "gemini-2.5-flash"

_OUTLINE_PROMPT = """\
You are an expert content strategist. Analyse the news content below and produce \
a Master Outline that will guide social media post generation across platforms.

BRAND CONTEXT:
{brand_context}

NEWS TITLE: {title}

NEWS CONTENT:
{content}

Return ONLY a valid JSON object — no markdown fences, no explanation — with this exact structure:
{{
  "core_message": "The single most important message (1–2 sentences)",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "mandatory_facts": {{"fact_name": "fact_value"}},
  "audience": "Who this content speaks to",
  "tone": "The specific tone to use for this piece"
}}

Rules:
- core_message must align with the brand context
- key_points: 3–5 actionable or informative points
- mandatory_facts: any numbers, stats, dates, or proper names that must not be altered
- tone must be consistent with the brand's primary and secondary tones
"""


class MasterOutline(BaseModel):
    core_message: str
    key_points: list[str]
    mandatory_facts: dict[str, str]
    audience: str
    tone: str


async def generate_master_outline(
    processed: ProcessedContent,
    trace_id: str,
) -> MasterOutline:
    """Call Gemini Flash to produce a validated MasterOutline."""
    prompt = _OUTLINE_PROMPT.format(
        brand_context=processed.brand_context,
        title=processed.title,
        content=processed.clean_content,
    )

    raw = await gemini_generate_json(prompt, GEMINI_FLASH_MODEL)
    data = json.loads(raw)
    outline = MasterOutline(**data)

    logger.info(
        "Master outline generated",
        extra={
            "trace_id": trace_id,
            "stage": "task_router",
            "core_message_preview": outline.core_message[:80],
            "key_point_count": len(outline.key_points),
        },
    )

    return outline
