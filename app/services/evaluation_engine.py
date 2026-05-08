# app/services/evaluation_engine.py
import json
from dataclasses import dataclass

from app.ai.gemini_client import gemini_generate_json
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

GEMINI_FLASH_MODEL = "gemini-2.5-flash"  # gemini-2.5-pro has 0 free-tier quota
MAX_RETRIES = 3

_PLATFORM_CONSTRAINTS = {
    "x": "≤280 characters total, strong hook, 0–1 emojis, 1–3 hashtags, punchy and concise",
    "linkedin": "150–300 words, professional tone, storytelling format, ends with engagement question, 3–5 hashtags",
    "facebook": "80–150 words, conversational and community-focused, ends with a question, 1–2 hashtags, 2–3 emojis",
}

_EVAL_PROMPT = """\
You are a senior content quality evaluator. Score the following {platform_upper} social media post.

POST:
{post_text}

BRAND CONTEXT:
{brand_context}

{platform_upper} REQUIREMENTS:
{platform_constraints}

Score each dimension from 0.0 to 1.0 (two decimal places):
1. brand_score — Alignment with brand voice, tone, core message, and prohibited content rules
2. human_likeness_score — Sounds natural and human, not robotic, generic, or AI-like
3. platform_compliance_score — Respects platform length, format, hashtag rules, and style guidelines

Return ONLY a valid JSON object — no markdown fences, no explanation:
{{
  "brand_score": 0.00,
  "human_likeness_score": 0.00,
  "platform_compliance_score": 0.00,
  "feedback": "Brief strengths and improvement notes (max 80 words)"
}}
"""


@dataclass
class EvaluationResult:
    brand_score: float
    human_likeness_score: float
    platform_compliance_score: float
    overall_score: float
    feedback: str
    passed: bool


async def evaluate_post(
    *,
    platform: str,
    post_text: str,
    brand_context: str,
    trace_id: str,
) -> EvaluationResult:
    """Evaluate a single platform post using Gemini 2.5 Pro."""
    prompt = _EVAL_PROMPT.format(
        platform_upper=platform.upper(),
        post_text=post_text,
        brand_context=brand_context,
        platform_constraints=_PLATFORM_CONSTRAINTS.get(platform, "standard social media best practices"),
    )

    raw = await gemini_generate_json(prompt, GEMINI_FLASH_MODEL)
    data = json.loads(raw)

    brand = float(data["brand_score"])
    human = float(data["human_likeness_score"])
    compliance = float(data["platform_compliance_score"])
    overall = round((brand + human + compliance) / 3, 4)
    passed = overall >= settings.eval_score_threshold

    result = EvaluationResult(
        brand_score=brand,
        human_likeness_score=human,
        platform_compliance_score=compliance,
        overall_score=overall,
        feedback=data.get("feedback", ""),
        passed=passed,
    )

    logger.info(
        "Evaluation complete",
        extra={
            "trace_id": trace_id,
            "stage": "evaluation",
            "platform": platform,
            "overall_score": overall,
            "decision": "PASS" if passed else "REGENERATE",
        },
    )

    return result
