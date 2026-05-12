"""
One-shot script to create all database tables from the SQLAlchemy models.
Run once: python create_tables.py
"""
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.db.models import ContentVersion, NewsItem  # noqa: F401 – ensures models are registered


async def main() -> None:
    print(f"Connecting to: {settings.database_url[:60]}...")
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("\n✅ Tables created successfully: news_items, content_versions")


if __name__ == "__main__":
    asyncio.run(main())
