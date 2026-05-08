# app/services/ayrshare_client.py
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

AYRSHARE_URL = "https://app.ayrshare.com/api/post"


async def post_to_ayrshare(post_text: str, platforms: list[str], media_urls: list[str] | None = None) -> dict | None:
    """
    Posts content to Ayrshare API.
    Platforms must be Ayrshare compatible names (e.g. 'twitter', 'linkedin', 'facebook').
    """
    if settings.mock_publishing or not settings.ayrshare_api_key or settings.ayrshare_api_key == "your_ayrshare_api_key_here" or settings.ayrshare_api_key == "place_holder_key":
        logger.warning(
            "Mock publishing enabled or Ayrshare API key not configured, skipping real API call",
            extra={"stage": "publishing", "decision": "SKIPPED"}
        )
        # Mock successful response for testing if no key is present
        return {
            "status": "success",
            "id": "mock_ayrshare_post_id",
            "postIds": [{"platform": p, "id": f"mock_{p}_id"} for p in platforms]
        }

    headers = {
        "Authorization": f"Bearer {settings.ayrshare_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "post": post_text,
        "platforms": platforms,
    }
    
    if media_urls:
        payload["mediaUrls"] = media_urls

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(AYRSHARE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            logger.info(
                "Successfully posted to Ayrshare",
                extra={
                    "stage": "publishing",
                    "ayrshare_id": data.get("id"),
                    "platforms": platforms
                }
            )
            return data
    except httpx.HTTPStatusError as e:
        logger.error(
            "Ayrshare API returned error",
            extra={
                "stage": "publishing",
                "status_code": e.response.status_code,
                "response": e.response.text
            }
        )
        raise
    except Exception as e:
        logger.error(
            "Ayrshare request failed",
            extra={
                "stage": "publishing",
                "error": str(e)
            }
        )
        raise
