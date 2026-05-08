# app/services/publishing_service.py
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.content_version_repository import ContentVersionRepository
from app.repositories.news_repository import NewsRepository
from app.services.ayrshare_client import post_to_ayrshare
from app.services.cloudinary_service import transform_and_upload_image

logger = get_logger(__name__)


def map_platform_for_ayrshare(platform: str) -> str:
    """Maps internal platform names to Ayrshare compatible names."""
    mapping = {
        "x": "twitter",
        "linkedin": "linkedin",
        "facebook": "facebook",
        "instagram": "instagram"
    }
    return mapping.get(platform.lower(), platform.lower())


async def publish_content_version(content_version_id: int) -> bool:
    """
    Retrieves the content version, verifies approval, posts to Ayrshare,
    and updates the database.
    """
    async with AsyncSessionLocal() as session:
        repo = ContentVersionRepository(session)
        cv = await repo.get_by_id(content_version_id)
        
        if not cv:
            logger.error("Content version not found for publishing", extra={"cv_id": content_version_id})
            return False
            
        if not cv.approved_by_human:
            logger.error("Attempted to publish unapproved content", extra={"cv_id": content_version_id})
            return False
            
        if cv.status == "PUBLISHED":
            logger.info("Content already published", extra={"cv_id": content_version_id})
            return True

        ayrshare_platform = map_platform_for_ayrshare(cv.platform)
        
        try:
            # Check for image and transform it
            news_repo = NewsRepository(session)
            news_item = await news_repo.get_by_id(cv.news_item_id)
            
            media_urls = []
            if news_item and news_item.image_url:
                transformed_url = await transform_and_upload_image(news_item.image_url)
                if transformed_url:
                    media_urls.append(transformed_url)
            
            # Post to Ayrshare
            result = await post_to_ayrshare(cv.content_text, [ayrshare_platform], media_urls)
            
            # Extract post ID
            post_id = result.get("id") if result else "mock_ayrshare_post_id"
            published_at = datetime.now(timezone.utc)
            
            # Update database
            await repo.update_publishing_info(
                cv_id=content_version_id,
                post_id=post_id,
                published_at=published_at
            )
            
            logger.info(
                "Successfully published content version", 
                extra={
                    "cv_id": content_version_id, 
                    "platform": cv.platform,
                    "ayrshare_post_id": post_id
                }
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to publish content version", 
                extra={
                    "cv_id": content_version_id, 
                    "error": str(e)
                }
            )
            return False
