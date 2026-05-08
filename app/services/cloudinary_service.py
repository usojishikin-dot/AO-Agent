# app/services/cloudinary_service.py
import asyncio
import cloudinary
import cloudinary.uploader

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize Cloudinary globally if configured
if settings.cloudinary_url and "place_holder" not in settings.cloudinary_url and "your_api_key" not in settings.cloudinary_url:
    cloudinary.config(url=settings.cloudinary_url)
else:
    logger.warning("Cloudinary URL not configured, media transformations will be skipped or mocked")


async def transform_and_upload_image(image_url: str) -> str:
    """
    Uploads an external image to Cloudinary and applies standard 
    social media optimizations (1200x630, auto format, auto quality).
    """
    if not settings.cloudinary_url or "place_holder" in settings.cloudinary_url or "your_api_key" in settings.cloudinary_url:
        logger.warning(
            "Cloudinary not configured, returning original image_url",
            extra={"stage": "media_layer", "decision": "SKIPPED"}
        )
        return image_url
        
    try:
        # Run the synchronous Cloudinary upload in a thread pool to avoid blocking the event loop
        def _upload():
            return cloudinary.uploader.upload(
                image_url,
                transformation=[
                    {'width': 1200, 'height': 630, 'crop': 'fill'},
                    {'fetch_format': 'auto', 'quality': 'auto'}
                ]
            )
            
        result = await asyncio.to_thread(_upload)
        secure_url = result.get("secure_url")
        
        logger.info(
            "Image transformed and uploaded to Cloudinary",
            extra={"stage": "media_layer", "original_url": image_url, "secure_url": secure_url}
        )
        return secure_url or image_url
        
    except Exception as e:
        logger.error(
            "Cloudinary transformation failed",
            extra={"stage": "media_layer", "error": str(e), "original_url": image_url}
        )
        return image_url # Fallback to original image if transformation fails
