import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from sqlalchemy import text
from app.db.base import Base
import app.db.models # Ensure models are loaded

async def main():
    print(f"Connecting to: {settings.database_url[:50]}...")
    engine = create_async_engine(settings.database_url)
    
    async with engine.begin() as conn:
        print("Creating 'organizations' table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS organizations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                website_url TEXT,
                webhook_token VARCHAR(255) UNIQUE NOT NULL,
                mission_statement TEXT,
                core_pillars TEXT,
                voice_parameters TEXT,
                gatekeeper_rules TEXT,
                brand_bible TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        
        print("Adding 'webhook_token' to 'organizations' table if needed...")
        await conn.execute(text('ALTER TABLE organizations ADD COLUMN IF NOT EXISTS webhook_token VARCHAR(255) UNIQUE'))
        
        print("Adding 'organization_id' to 'users' table...")
        await conn.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)'))
        
        print("Adding 'role' to 'users' table...")
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'editor'"))
        
        print("Adding 'organization_id' to 'news_items' table...")
        await conn.execute(text('ALTER TABLE news_items ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)'))
        
    await engine.dispose()
    print("[OK] Multi-tenant migration successful!")

if __name__ == "__main__":
    asyncio.run(main())
