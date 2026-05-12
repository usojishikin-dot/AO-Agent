# app/repositories/news_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NewsItem


class NewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_external_id(self, external_id: str) -> NewsItem | None:
        stmt = select(NewsItem).where(NewsItem.external_id == external_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, news_item_id: int) -> NewsItem | None:
        stmt = select(NewsItem).where(NewsItem.id == news_item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, news_item_id: int, status: str) -> None:
        item = await self.get_by_id(news_item_id)
        if item:
            item.status = status
            await self.session.commit()

    async def update_master_outline(self, news_item_id: int, outline: str) -> None:
        item = await self.get_by_id(news_item_id)
        if item:
            item.master_outline = outline
            await self.session.commit()

    async def update_image_url(self, news_item_id: int, image_url: str) -> None:
        item = await self.get_by_id(news_item_id)
        if item:
            item.image_url = image_url
            await self.session.commit()

    async def create_news_item(
        self,
        *,
        organization_id: int | None = None,
        external_id: str,
        title: str,
        content: str,
        source_url: str | None,
        image_url: str | None,
        trace_id: str,
        status: str = "RECEIVED",
    ) -> NewsItem:
        item = NewsItem(
            organization_id=organization_id,
            external_id=external_id,
            title=title,
            content=content,
            source_url=source_url,
            image_url=image_url,
            status=status,
            trace_id=trace_id,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def list_news_items(self, organization_id: int | None = None) -> list[NewsItem]:
        stmt = select(NewsItem)
        if organization_id:
            stmt = stmt.where(NewsItem.organization_id == organization_id)
        stmt = stmt.order_by(NewsItem.id.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())