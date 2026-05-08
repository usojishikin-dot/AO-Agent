from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db_session
from app.db.models import ContentVersion, NewsItem

router = APIRouter(tags=["analytics"])

@router.get("/analytics/stats")
async def get_analytics_stats(
    session: AsyncSession = Depends(get_db_session),
):
    # Total Posts (Published)
    published_stmt = select(func.count(ContentVersion.id)).where(ContentVersion.status == "PUBLISHED")
    published_count = (await session.execute(published_stmt)).scalar() or 0

    # Total Generated (Queue)
    queue_stmt = select(func.count(ContentVersion.id)).where(ContentVersion.status == "GENERATED")
    queue_count = (await session.execute(queue_stmt)).scalar() or 0

    # Platform counts for "Best Platform" logic
    platform_stmt = (
        select(ContentVersion.platform, func.count(ContentVersion.id))
        .where(ContentVersion.status == "PUBLISHED")
        .group_by(ContentVersion.platform)
    )
    platform_counts = (await session.execute(platform_stmt)).all()
    
    best_platform = "N/A"
    highest_count = -1
    platform_data = {"linkedin": 0, "x": 0, "facebook": 0}
    
    for platform, count in platform_counts:
        platform_data[platform.lower()] = count
        if count > highest_count:
            highest_count = count
            best_platform = platform.capitalize()
            if platform.lower() == 'x':
                best_platform = "X (Twitter)"

    # Total reach & engagement are simulated for the MVP based on volume
    total_reach = f"{(published_count * 1.5):.1f}K" if published_count > 0 else "0"
    engagement_rate = "4.8%" if published_count > 0 else "0%"

    return {
        "total_published": published_count,
        "total_queued": queue_count,
        "total_reach": total_reach,
        "engagement_rate": engagement_rate,
        "best_platform": best_platform,
        "platform_data": platform_data
    }
