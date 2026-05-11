# app/services/generation_engine.py
import asyncio
from functools import lru_cache
from pathlib import Path

import yaml

from app.ai.groq_client import groq_generate
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.content_version_repository import ContentVersionRepository
from app.services.task_router import MasterOutline

logger = get_logger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"
BRAND_BIBLE_PATH = Path(__file__).parent.parent.parent / "brand_bible.yaml"


@lru_cache(maxsize=1)
def _load_bible() -> dict:
    if not BRAND_BIBLE_PATH.exists():
        return {}
    with BRAND_BIBLE_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _platform_constraints(bible: dict) -> dict[str, dict[str, str]]:
    """Build per-platform constraint dicts from the brand bible."""
    hp = bible.get("hashtag_policy", {})
    pn = bible.get("platform_notes", {})
    approved = ", ".join(h for h in (hp.get("approved_hashtags") or []) if h) or "relevant hashtags"

    return {
        "x": {
            "char_limit": "≤280 characters total",
            "length_guide": "short and punchy",
            "hashtag_rule": f"max {hp.get('max_hashtags_x', 3)} hashtags — choose from: {approved}",
            "style": pn.get("x", {}).get("style", "strong hook, concise, impactful"),
            "emoji": pn.get("x", {}).get("emoji_use", "0–1 emojis max"),
        },
        "linkedin_company": {
            "char_limit": "150–300 words",
            "length_guide": "medium, insight-driven",
            "hashtag_rule": f"max {hp.get('max_hashtags_linkedin', 5)} hashtags — choose from: {approved}",
            "style": pn.get("linkedin", {}).get("style", "professional storytelling, brand-focused, use 'We'/'Our', end with a question"),
            "emoji": pn.get("linkedin", {}).get("emoji_use", "very subtle use"),
            "voice_directive": "Write from the brand's collective perspective. Use 'We', 'Our team', or the organization's name. Polished, authoritative, and brand-aligned.",
        },
        "linkedin_personal": {
            "char_limit": "150–300 words",
            "length_guide": "medium, thought-leadership",
            "hashtag_rule": f"max {hp.get('max_hashtags_linkedin', 5)} hashtags — choose from: {approved}",
            "style": "Thought-leadership, first-person narrative using 'I'/'My', open with a visionary or contrarian hook, end with a personal reflection or call-to-action",
            "emoji": pn.get("linkedin", {}).get("emoji_use", "very subtle use"),
            "voice_directive": "Write from the CEO/Founder's personal perspective. Use 'I', 'My', 'In my view'. Be opinionated, visionary, and direct. This is a personal post, not a brand post.",
        },
        "facebook": {
            "char_limit": "80–150 words",
            "length_guide": "conversational",
            "hashtag_rule": f"max {hp.get('max_hashtags_facebook', 2)} hashtags — choose from: {approved}",
            "style": pn.get("facebook", {}).get("style", "community-focused, end with a direct question"),
            "emoji": pn.get("facebook", {}).get("emoji_use", "friendly, 2–3 emojis"),
        },
    }


_POST_PROMPT = """\
You are an expert social media copywriter. Write a {platform_upper} post based strictly on the outline below.

MASTER OUTLINE:
- Core Message: {core_message}
- Key Points:
{key_points_formatted}
- Mandatory Facts (do NOT alter these): {mandatory_facts}
- Target Audience: {audience}
- Tone: {tone}

{platform_upper} PLATFORM REQUIREMENTS:
- Length: {char_limit} ({length_guide})
- Hashtags: {hashtag_rule}
- Style: {style}
- Emoji usage: {emoji}

VOICE MEMORY (Examples of successful past posts to emulate):
{voice_memory}

CRITICAL RULES:
- Write in a natural, human tone — avoid AI-sounding, corporate, or generic openers
- Do NOT start with "Hey", "Excited to share", "I am pleased to", or similar clichés
- Use all mandatory facts exactly as given
- Return ONLY the post text — no labels, no markdown, no explanation
"""

_REFINE_PROMPT = """\
You are an expert social media copywriter. You have been asked to refine a {platform_upper} post based on specific feedback.

ORIGINAL POST:
{original_text}

FEEDBACK/REFINEMENT INSTRUCTIONS:
{refinement_instructions}

{platform_upper} PLATFORM REQUIREMENTS:
- Length: {char_limit} ({length_guide})
- Hashtags: {hashtag_rule}
- Style: {style}
- Emoji usage: {emoji}

CRITICAL RULES:
- Fix the issues mentioned in the feedback while maintaining the core message.
- Maintain a natural, human tone.
- Return ONLY the refined post text — no labels, no markdown, no explanation.
"""


async def _generate_one(
    platform: str,
    outline: MasterOutline,
    constraints: dict[str, dict[str, str]],
    trace_id: str,
) -> tuple[str, str]:
    """Generate a post for one platform. Returns (platform, post_text)."""
    c = constraints[platform]
    key_points_formatted = "\n".join(f"  • {p}" for p in outline.key_points)
    mandatory_facts = str(outline.mandatory_facts) if outline.mandatory_facts else "None"

    # Voice directive is an optional extra instruction injected for LinkedIn variants
    voice_directive = c.get("voice_directive", "")
    voice_directive_block = f"\nVOICE DIRECTIVE:\n{voice_directive}\n" if voice_directive else ""

    # Fetch Voice Memory (fall back gracefully if platform key not yet in DB)
    voice_memory_text = "None available yet."
    try:
        async with AsyncSessionLocal() as session:
            repo = ContentVersionRepository(session)
            past_posts = await repo.get_voice_memory(platform)
            if past_posts:
                voice_memory_text = "\n\n".join(f"---\n{p.content_text}" for p in past_posts)
    except Exception as e:
        logger.error("Failed to fetch voice memory", extra={"error": str(e), "trace_id": trace_id})

    prompt = _POST_PROMPT.format(
        platform_upper=platform.upper(),
        core_message=outline.core_message,
        key_points_formatted=key_points_formatted,
        mandatory_facts=mandatory_facts,
        audience=outline.audience,
        tone=outline.tone,
        char_limit=c["char_limit"],
        length_guide=c["length_guide"],
        hashtag_rule=c["hashtag_rule"],
        style=c["style"],
        emoji=c["emoji"],
        voice_memory=voice_memory_text,
    ) + voice_directive_block

    text = await groq_generate(prompt, GROQ_MODEL)
    text = text.strip()

    logger.info(
        "Post generated",
        extra={
            "trace_id": trace_id,
            "stage": "generation",
            "platform": platform,
            "char_count": len(text),
        },
    )
    return platform, text


async def generate_all_platforms(
    outline: MasterOutline,
    trace_id: str,
) -> dict[str, str]:
    """Generate posts for X, LinkedIn Company, LinkedIn Personal, and Facebook concurrently."""
    bible = _load_bible()
    constraints = _platform_constraints(bible)

    results = await asyncio.gather(
        _generate_one("x", outline, constraints, trace_id),
        _generate_one("linkedin_company", outline, constraints, trace_id),
        _generate_one("linkedin_personal", outline, constraints, trace_id),
        _generate_one("facebook", outline, constraints, trace_id),
    )

    logger.info(
        "All platforms generated",
        extra={"trace_id": trace_id, "stage": "generation"},
    )
    return dict(results)


async def regenerate_one_platform(
    platform: str,
    outline: MasterOutline,
    trace_id: str,
) -> str:
    """Regenerate a single platform post (used during evaluation retry)."""
    bible = _load_bible()
    constraints = _platform_constraints(bible)
    _, text = await _generate_one(platform, outline, constraints, trace_id)
    return text


async def refine_one_platform(
    platform: str,
    original_text: str,
    refinement_instructions: str,
    trace_id: str,
) -> str:
    """Refine a single platform post using feedback (agentic reflection)."""
    bible = _load_bible()
    constraints = _platform_constraints(bible)
    c = constraints[platform]

    prompt = _REFINE_PROMPT.format(
        platform_upper=platform.upper(),
        original_text=original_text,
        refinement_instructions=refinement_instructions,
        char_limit=c["char_limit"],
        length_guide=c["length_guide"],
        hashtag_rule=c["hashtag_rule"],
        style=c["style"],
        emoji=c["emoji"],
    )

    text = await groq_generate(prompt, GROQ_MODEL)
    text = text.strip()

    logger.info(
        "Post refined",
        extra={
            "trace_id": trace_id,
            "stage": "generation",
            "platform": platform,
            "char_count": len(text),
        },
    )
    return text
