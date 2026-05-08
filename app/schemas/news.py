# app/schemas/news.py
from pydantic import BaseModel, Field, HttpUrl, field_validator


class NewsTriggerRequest(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    source_url: HttpUrl | None = None
    image_url: HttpUrl | None = None

    @field_validator("external_id", "title", "content")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace")
        return cleaned

class NewsItemResponse(BaseModel):
    id: int
    external_id: str
    title: str
    content: str
    source_url: str | None
    image_url: str | None
    status: str
    master_outline: str | None = None
    trace_id: str