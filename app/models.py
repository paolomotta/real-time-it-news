from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class NewsItem(BaseModel):
    id: str = Field(..., description="Unique identifier for the news item")
    source: str = Field(..., description="Origin of the news item (e.g., 'reddit', 'arstechnica')")
    title: str = Field(..., description="Title or headline of the news article")
    body: Optional[str] = Field(default="", description="Optional body or summary of the news article")
    published_at: datetime = Field(..., description="UTC timestamp of when the news item was published")
    relevance_score: Optional[float] = Field(default=None, exclude=True)

    model_config = ConfigDict(
        extra="forbid", # Forbid extra fields not defined in the model
        json_schema_extra={
            "example": {
                "id": "reddit-abc123",
                "source": "reddit",
                "title": "Critical vulnerability found in OpenSSL",
                "body": "A major vulnerability has been disclosed...",
                "published_at": "2025-06-14T09:00:00Z"
            }
        }
    )