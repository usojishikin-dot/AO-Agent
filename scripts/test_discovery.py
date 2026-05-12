import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.services.onboarding_service import OnboardingService

async def test_discovery(url: str):
    print(f"\n--- Starting Discovery Agent for: {url} ---")
    service = OnboardingService()
    
    print("Step 1: Scraping and analyzing... (This may take a few seconds)")
    result = await service.onboard_from_url(url)
    
    if "error" in result:
        print(f"FAILED: {result['error']}")
        return

    print("\n--- Discovery Successful! ---")
    print(f"Organization: {result.get('organization_name')}")
    print(f"Mission: {result.get('mission_statement')}")
    print(f"Core Pillars: {', '.join(result.get('core_pillars', []))}")
    print(f"Voice Tone: {result.get('voice_parameters', {}).get('tone')}")
    print(f"Target Audience: {result.get('voice_parameters', {}).get('audience')}")
    print(f"Gatekeeper Rules: {result.get('gatekeeper_rules')}")
    print("\n------------------------------")

if __name__ == "__main__":
    # Test with a high-impact organization URL
    test_url = "https://www.charitywater.org/about" 
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    asyncio.run(test_discovery(test_url))
