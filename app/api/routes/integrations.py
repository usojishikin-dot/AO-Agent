from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["integrations"])

class ProfileLinkResponse(BaseModel):
    url: str

@router.get("/integrations/ayrshare/profile-link", response_model=ProfileLinkResponse)
async def get_ayrshare_profile_link(title: str = "Client Profile"):
    """
    Generates a JWT profile link URL from Ayrshare. 
    If the API key is missing or invalid, it falls back to the main Ayrshare dashboard.
    """
    if not settings.ayrshare_api_key or settings.ayrshare_api_key == "your_ayrshare_api_key_here":
        return ProfileLinkResponse(url="https://app.ayrshare.com/")

    headers = {
        "Authorization": f"Bearer {settings.ayrshare_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post("https://app.ayrshare.com/api/profiles/generateJWT", headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return ProfileLinkResponse(url=data.get("url", "https://app.ayrshare.com/"))
            else:
                logger.error(f"Failed to generate Ayrshare JWT: {response.text}")
                return ProfileLinkResponse(url="https://app.ayrshare.com/")
                
    except Exception as e:
        logger.error(f"Error connecting to Ayrshare: {str(e)}")
        return ProfileLinkResponse(url="https://app.ayrshare.com/")
