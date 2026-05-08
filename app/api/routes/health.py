# app/api/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db_session

router = APIRouter(tags=["health"])

from app.core.config import settings

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Enterprise AI Social Media Factory"}

@router.get("/integration-config")
async def get_integration_config():
    """Returns the integration details for the dashboard to display."""
    return {
        "webhook_url": "/news-trigger", 
        "token": settings.webhook_bearer_token
    }

@router.get("/run-migration")
async def run_migration(session: AsyncSession = Depends(get_db_session)):
    """
    Temporary route to run database migrations from the browser.
    Integrates Supabase Agent Skills: RLS activation and explicit grants.
    """
    try:
        # 1. Add missing columns
        await session.execute(text('ALTER TABLE news_items ADD COLUMN IF NOT EXISTS master_outline TEXT'))
        
        # 2. Enable RLS (Security Best Practice from agent-skills)
        await session.execute(text('ALTER TABLE news_items ENABLE ROW LEVEL SECURITY'))
        await session.execute(text('ALTER TABLE content_versions ENABLE ROW LEVEL SECURITY'))
        
        # 3. Grant permissions (Required for PostgREST API if used)
        await session.execute(text('GRANT ALL ON TABLE news_items TO authenticated'))
        await session.execute(text('GRANT ALL ON TABLE news_items TO anon'))
        await session.execute(text('GRANT ALL ON TABLE content_versions TO authenticated'))
        await session.execute(text('GRANT ALL ON TABLE content_versions TO anon'))
        
        # 4. Add a basic permissive policy for now (since we're in dev)
        # In production, these should be restricted to auth.uid()
        await session.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all for now') THEN CREATE POLICY \"Allow all for now\" ON news_items FOR ALL USING (true); END IF; END $$"))
        await session.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all for now') THEN CREATE POLICY \"Allow all for now\" ON content_versions FOR ALL USING (true); END IF; END $$"))
        
        await session.commit()
        return {
            "status": "success", 
            "message": "Migration complete: Column added, RLS enabled, and permissions granted!"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
