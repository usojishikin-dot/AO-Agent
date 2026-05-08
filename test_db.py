import asyncio
from app.db.session import AsyncSessionLocal
from app.repositories.news_repository import NewsRepository

async def test():
    async with AsyncSessionLocal() as session:
        repo = NewsRepository(session)
        items = await repo.list_news_items()
        print(f"Found {len(items)} items via repository")
        for item in items:
            print(f"  ID={item.id}, title={item.title}, status={item.status}")

asyncio.run(test())
