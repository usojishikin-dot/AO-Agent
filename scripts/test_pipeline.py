import os
import sys
import uuid
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def main():
    # Attempt to load from .env, fallback to user input
    token = os.getenv("WEBHOOK_BEARER_TOKEN")
    if not token:
        token = input("Enter your WEBHOOK_BEARER_TOKEN: ").strip()

    # Default to local, but allow testing against production
    default_url = "http://localhost:8000"
    base_url = input(f"Enter backend URL (Press Enter to use {default_url}): ").strip()
    if not base_url:
        base_url = default_url

    webhook_url = f"{base_url}/news-trigger"

    print("\nEnterprise AI Social Media Factory - E2E Tester")
    print(f"Targeting: {webhook_url}\n")

    # Sample Development & Impact News Item
    payload = {
        "external_id": f"test-post-{uuid.uuid4().hex[:8]}",
        "title": "Global Impact Initiative Secures $50M for Sustainable Water Projects",
        "content": "A new partnership between international development agencies and local NGOs has successfully raised $50M to implement sustainable water solutions across sub-Saharan Africa. The initiative aims to provide clean water access to over 2 million people by 2028, focusing on community-led management and innovative solar-powered pumping systems. This funding marks a significant milestone in regional collaborative efforts for sustainable development.",
        "source_url": "https://impact-news.com/sustainable-water-initiative",
        "image_url": "https://images.unsplash.com/photo-1541544741938-0af808b9323b"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        print("Sending payload to ingestion engine...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=payload, headers=headers)
            
            if response.status_code == 202:
                data = response.json()
                print("\nSUCCESS: Pipeline Triggered!")
                print(f"Trace ID: {data.get('trace_id')}")
                print(f"Status: {data.get('status')}")
                print(f"Message: {data.get('message')}")
                print("\n➡️ Next Steps: Open your Next.js Dashboard, navigate to the 'Queue' tab, and watch the AI posts arrive!")
            elif response.status_code == 401:
                print("\nERROR: Unauthorized. Your WEBHOOK_BEARER_TOKEN is incorrect.")
            else:
                print(f"\nERROR: Pipeline failed with status code {response.status_code}")
                print(response.text)

    except httpx.ConnectError:
        print(f"\nERROR: Could not connect to {base_url}. Is the FastAPI server running?")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
