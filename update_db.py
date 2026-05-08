import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from sqlalchemy import text

async def main():
    print(f"Connecting to: {settings.database_url[:50]}...")
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        print("Adding column 'master_outline' if it doesn't exist...")
        await conn.execute(text('ALTER TABLE news_items ADD COLUMN IF NOT EXISTS master_outline TEXT'))
    await engine.dispose()
    print("✅ Database updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
