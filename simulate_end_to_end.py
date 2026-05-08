import asyncio
import httpx
import uuid
import time
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import ContentVersion, NewsItem
from app.core.config import settings

API_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": f"Bearer {settings.webhook_bearer_token}"}

async def run_simulation():
    print("🚀 Starting End-to-End Simulation...")
    print("Make sure you have running: uvicorn app.main:app --reload\n")
    
    external_id = f"sim-{uuid.uuid4().hex[:8]}"
    
    # 1. Trigger the news ingestion
    payload = {
        "external_id": external_id,
        "title": "Kove Content House Reaches 1M Users!",
        "content": "We are thrilled to announce that Kove Content House has officially crossed 1 million active users this week. This milestone proves that AI-driven content is the future of marketing.",
        "source_url": "https://kove.com/milestone",
        # Providing a real image to test Cloudinary
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80"
    }
    
    print(f"📡 [1] Sending Webhook for NewsItem ({external_id})...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/news-trigger", json=payload, headers=HEADERS)
            response.raise_for_status()
            print("✅ Webhook accepted:", response.json())
        except Exception as e:
            print("❌ Webhook failed. Is the server running? Run `uvicorn app.main:app` in another terminal.")
            return

    # 2. Wait for AI Pipeline to finish
    print("\n⏳ [2] Waiting for AI Pipeline to generate content (Groq + Gemini)...")
    await asyncio.sleep(20) # Give it 20 seconds
    
    # 3. Retrieve Generated Content from DB
    print("\n💾 [3] Fetching Generated Content from Database...")
    cv_id_to_approve = None
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ContentVersion).join(NewsItem).where(NewsItem.external_id == external_id)
        )
        versions = result.scalars().all()
        
        if not versions:
            print("❌ No content versions found. Pipeline might have failed or is still running.")
            return
            
        print(f"✅ Found {len(versions)} generated posts!")
        for v in versions:
            print(f"\n--- Platform: {v.platform} | Score: {v.evaluation_score} ---")
            print(v.content_text)
            print("-" * 40)
            
        # Select the best scoring post
        best_post = max(versions, key=lambda x: x.evaluation_score or 0)
        cv_id_to_approve = best_post.id
        print(f"\n🎯 Selected best post (ID: {cv_id_to_approve}, Platform: {best_post.platform}) for approval.")

    # 4. Trigger Approval & Publishing
    if cv_id_to_approve:
        print("\n🚀 [4] Approving post and triggering Cloudinary + Mock Publishing...")
        async with httpx.AsyncClient() as client:
            try:
                # We do NOT pass headers here because the approval endpoint currently isn't protected by the bearer token
                response = await client.post(f"{API_URL}/content-versions/{cv_id_to_approve}/approve")
                response.raise_for_status()
                print("✅ Approval accepted:", response.json())
            except Exception as e:
                print("❌ Approval failed:", e)

    print("\n🎉 Simulation complete! Check your server logs to see the Cloudinary upload and mock Ayrshare payload.")

if __name__ == "__main__":
    asyncio.run(run_simulation())
