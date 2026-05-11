from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreateContentVersionRequest(BaseModel):
    news_item_id: int = Field(gt=0)
    platform: str = Field(min_length=1, max_length=50)
    content_text: str = Field(min_length=1)


class ContentVersionResponse(BaseModel):
    id: int
    news_item_id: int
    platform: str
    version_number: int
    content_text: str
    status: str
    
    evaluation_score: Optional[float] = None
    brand_score: Optional[float] = None
    human_likeness_score: Optional[float] = None
    platform_compliance_score: Optional[float] = None
    evaluation_feedback: Optional[str] = None
    
    approved_by_human: bool = False
    ayrshare_post_id: Optional[str] = None
    published_at: Optional[datetime] = None

    # Joined fields
    news_item_title: Optional[str] = None
    news_item_image: Optional[str] = None