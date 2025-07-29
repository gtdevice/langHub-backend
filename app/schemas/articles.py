from datetime import datetime

from pydantic import BaseModel, Json
from typing import Optional, Dict, Any

class AdaptedArticleData(BaseModel):
    id: int
    original_article_id: int
    language: str
    level: str
    title: str
    thumbnail_url: Optional[str] = None
    intro: str
    adapted_text: str
    metadata: Dict[str, Any] #here was Json[]
    dialogue_starter_question: str

class DiscoverArticleData(BaseModel):
    title: str
    thumbnail_url: Optional[str] = None
    intro: str
    adapted_article_id: int
    dialogue_id: Optional[str] = None
    created_at: Optional[datetime] = None