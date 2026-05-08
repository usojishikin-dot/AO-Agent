# app/services/prompt_processor.py
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from app.core.logging import get_logger

logger = get_logger(__name__)

BRAND_BIBLE_PATH = Path(__file__).parent.parent.parent / "brand_bible.yaml"


@lru_cache(maxsize=1)
def _load_brand_bible() -> dict:
    """Load and cache the brand bible from YAML. Called once at first use."""
    if not BRAND_BIBLE_PATH.exists():
        logger.warning("brand_bible.yaml not found — using empty brand context",
                       extra={"stage": "prompt_processor"})
        return {}
    with BRAND_BIBLE_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _format_brand_context(bible: dict) -> str:
    """Flatten the brand bible dict into a clean prompt-injectable string."""
    lines: list[str] = []

    brand = bible.get("brand", {})
    if brand.get("name"):
        lines.append(f"Organization: {brand['name']}")
    if brand.get("tagline"):
        lines.append(f"Tagline: {brand['tagline']}")

    vt = bible.get("voice_and_tone", {})
    if vt.get("primary_tone"):
        lines.append(f"Primary Tone: {vt['primary_tone']}")
    if vt.get("secondary_tone"):
        lines.append(f"Secondary Tone: {vt['secondary_tone']}")
    traits = [t for t in (vt.get("personality_traits") or []) if t]
    if traits:
        lines.append(f"Personality Traits: {', '.join(traits)}")
    if vt.get("writing_style"):
        lines.append(f"Writing Style: {vt['writing_style']}")

    audience = bible.get("audience", {})
    if audience.get("primary"):
        lines.append(f"Primary Audience: {audience['primary']}")
    if audience.get("secondary"):
        lines.append(f"Secondary Audience: {audience['secondary']}")

    messaging = bible.get("messaging", {})
    if messaging.get("core_message"):
        lines.append(f"Core Brand Message: {messaging['core_message']}")
    diffs = [d for d in (messaging.get("key_differentiators") or []) if d]
    if diffs:
        lines.append(f"Key Differentiators: {'; '.join(diffs)}")

    prohibited = bible.get("prohibited", {})
    banned: list[str] = []
    for key in ("words", "phrases", "topics"):
        banned.extend(i for i in (prohibited.get(key) or []) if i)
    if banned:
        lines.append(f"NEVER USE OR MENTION: {', '.join(banned)}")

    ctas = bible.get("calls_to_action", {})
    if ctas.get("primary_cta"):
        lines.append(f"Primary CTA: {ctas['primary_cta']}")
    if ctas.get("secondary_cta"):
        lines.append(f"Secondary CTA: {ctas['secondary_cta']}")

    hp = bible.get("hashtag_policy", {})
    approved = [h for h in (hp.get("approved_hashtags") or []) if h]
    if approved:
        lines.append(f"Approved Hashtags: {', '.join(approved)}")

    return "\n".join(lines)


@dataclass
class ProcessedContent:
    title: str
    clean_content: str
    brand_context: str
    source_url: str | None
    image_url: str | None


def process_content(
    *,
    title: str,
    content: str,
    source_url: str | None = None,
    image_url: str | None = None,
) -> ProcessedContent:
    """Strip content, inject brand context, return ProcessedContent."""
    clean = re.sub(r"\n{3,}", "\n\n", content.strip())
    clean = re.sub(r"[ \t]+", " ", clean)

    bible = _load_brand_bible()
    brand_context = _format_brand_context(bible)

    logger.info("Content processed", extra={"stage": "prompt_processor"})

    return ProcessedContent(
        title=title.strip(),
        clean_content=clean,
        brand_context=brand_context,
        source_url=source_url,
        image_url=image_url,
    )
