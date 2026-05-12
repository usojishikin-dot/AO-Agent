import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio
from app.ai.gemini_client import gemini_generate_text
from app.core.config import settings

class ScraperService:
    @staticmethod
    async def fetch_text_from_url(url: str) -> str:
        """Fetches a URL and returns clean text from the body."""
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Remove scripts, styles, and other noise
                for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
                    script_or_style.decompose()
                
                # Extract text
                text = soup.get_text(separator=' ', strip=True)
                return text[:10000] # Limit to 10k chars for the LLM
            except Exception as e:
                print(f"Scraping error for {url}: {e}")
                return ""

class DiscoveryService:
    async def discover_organization_identity(self, website_url: str, scraped_text: str) -> Dict:
        """Analyzes scraped text to generate an Organization Identity Map."""
        prompt = f"""
        Analyze the following text scraped from {website_url}. 
        Synthesize a comprehensive 'Organization Identity Map' for an AI Content Factory.
        
        SCRAPED CONTENT:
        {scraped_text}
        
        OUTPUT FORMAT (JSON):
        {{
            "organization_name": "Name of the org",
            "mission_statement": "One sentence summary of what they do",
            "core_pillars": ["Pillar 1", "Pillar 2", "Pillar 3"],
            "voice_parameters": {{
                "tone": "Formal/Professional/Casual/Visionary",
                "vocabulary": "Key terms they use often",
                "audience": "Who they are talking to"
            }},
            "gatekeeper_rules": "Specific instructions on what content is relevant (e.g., 'Only post about water sustainability, ignore general tech news')"
        }}
        
        Focus on identifying what makes this organization unique and what kind of social media content would be MOST relevant to them.
        """
        
        try:
            # Use Gemini Flash for discovery (fast and cheap)
            response = await gemini_generate_text(prompt, model="gemini-2.5-flash")
            
            # Simple JSON extraction (assuming Gemini outputs clean JSON)
            import json
            import re
            
            # Clean up potential markdown formatting
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {{"error": "Failed to parse discovery JSON", "raw": response}}
            
        except Exception as e:
            return {{"error": str(e)}}

class OnboardingService:
    def __init__(self):
        self.scraper = ScraperService()
        self.discovery = DiscoveryService()

    async def onboard_from_url(self, url: str) -> Dict:
        """Full onboarding flow: Scrape -> Analyze -> Map."""
        # In a real version, we'd crawl multiple pages (About, Home, Services)
        # For this local test, we start with the main URL
        text = await self.scraper.fetch_text_from_url(url)
        if not text:
            return {{"error": "Could not scrape the website. Please check the URL."}}
            
        identity_map = await self.discovery.discover_organization_identity(url, text)
        return identity_map
