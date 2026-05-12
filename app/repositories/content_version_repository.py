from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ContentVersion


class ContentVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_content_version(
        self,
        *,
        news_item_id: int,
        platform: str,
        version_number: int,
        content_text: str,
        status: str = "GENERATED",
    ) -> ContentVersion:
        item = ContentVersion(
            news_item_id=news_item_id,
            platform=platform,
            version_number=version_number,
            content_text=content_text,
            status=status,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def create_content_version_with_scores(
        self,
        *,
        news_item_id: int,
        platform: str,
        version_number: int,
        content_text: str,
        status: str,
        evaluation_score: float,
        brand_score: float,
        human_likeness_score: float,
        platform_compliance_score: float,
        evaluation_feedback: str,
    ) -> ContentVersion:
        item = ContentVersion(
            news_item_id=news_item_id,
            platform=platform,
            version_number=version_number,
            content_text=content_text,
            status=status,
            evaluation_score=evaluation_score,
            brand_score=brand_score,
            human_likeness_score=human_likeness_score,
            platform_compliance_score=platform_compliance_score,
            evaluation_feedback=evaluation_feedback,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def list_by_news_item(self, news_item_id: int) -> list[ContentVersion]:
        stmt = (
            select(ContentVersion)
            .where(ContentVersion.news_item_id == news_item_id)
            .order_by(ContentVersion.platform, ContentVersion.version_number.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_status(self, status: str, organization_id: int | None = None) -> list[ContentVersion]:
        from sqlalchemy.orm import joinedload
        from app.db.models import NewsItem
        
        stmt = (
            select(ContentVersion)
            .options(joinedload(ContentVersion.news_item))
            .where(ContentVersion.status == status)
        )
        
        if organization_id:
            stmt = stmt.join(NewsItem).where(NewsItem.organization_id == organization_id)
            
        stmt = stmt.order_by(ContentVersion.published_at.desc(), ContentVersion.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_version_number(self, news_item_id: int, platform: str) -> int:
        stmt = (
            select(func.max(ContentVersion.version_number))
            .where(ContentVersion.news_item_id == news_item_id)
            .where(ContentVersion.platform == platform)
        )
        result = await self.session.execute(stmt)
        value = result.scalar_one()
        return value or 0

    async def get_by_id(self, cv_id: int) -> ContentVersion | None:
        stmt = select(ContentVersion).where(ContentVersion.id == cv_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_approved(self, cv_id: int) -> bool:
        stmt = (
            update(ContentVersion)
            .where(ContentVersion.id == cv_id)
            .values(approved_by_human=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def update_publishing_info(
        self, cv_id: int, post_id: str, published_at: datetime
    ) -> bool:
        stmt = (
            update(ContentVersion)
            .where(ContentVersion.id == cv_id)
            .values(
                ayrshare_post_id=post_id,
                published_at=published_at,
                status="PUBLISHED"
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_voice_memory(self, platform: str, organization_id: int | None = None, limit: int = 2) -> list[ContentVersion]:
        """Fetch previously generated, high-scoring posts for few-shot examples."""
        from app.db.models import NewsItem
        
        stmt = (
            select(ContentVersion)
            .where(ContentVersion.platform == platform)
            .where(ContentVersion.status.in_(["PUBLISHED", "GENERATED"]))
            .where(ContentVersion.evaluation_score != None)
        )
        
        if organization_id:
            stmt = stmt.join(NewsItem).where(NewsItem.organization_id == organization_id)
            
        stmt = stmt.order_by(ContentVersion.evaluation_score.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())