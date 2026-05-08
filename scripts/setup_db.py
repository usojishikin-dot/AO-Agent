import asyncio
from app.db.session import engine
from app.db.base import Base
# Ensure all models are imported so Base knows about them
import app.db.models

async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(setup())
