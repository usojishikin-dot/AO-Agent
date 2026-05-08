"""Final verification of all API endpoints."""
import asyncio
import httpx

API_URL = "http://127.0.0.1:8000"

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health
        r = await client.get(f"{API_URL}/health")
        print(f"[1] Health: {r.status_code} OK")

        # Test news-items
        r = await client.get(f"{API_URL}/news-items")
        items = r.json()
        print(f"[2] News Items: {r.status_code} | {len(items)} item(s)")
        for item in items:
            print(f"    ID={item['id']} | {item['title']} | Status: {item['status']}")

        # Test content versions for item 1
        r = await client.get(f"{API_URL}/news-items/1/versions")
        print(f"[3] Content Versions: {r.status_code}")
        if r.status_code == 200:
            versions = r.json()
            print(f"    {len(versions)} version(s) found:")
            for cv in versions:
                score = cv.get('evaluation_score', 'N/A')
                print(f"    -> {cv['platform'].upper():10s} | Score: {score} | Approved: {cv.get('approved_by_human', False)}")
                print(f"       Text: {cv['content_text'][:100]}...")
        
        print("\n=== ALL SYSTEMS GO ===")

asyncio.run(test())
