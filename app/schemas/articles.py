from pydantic import BaseModel, Json
from typing import Optional, Dict, Any

class ArticleListItem(BaseModel):
    articleId: str
    title: str
    introText: str
    thumbnail: str
    category: Optional[str] = None
    language: str
    level: str

class AdaptedArticleCreate(BaseModel):
    original_article_id: int
    language: str
    level: str
    title: str
    thumbnail_url: Optional[str] = None
    intro: str
    adapted_text: str
    metadata: Json[Dict[str, Any]]
    dialogue_starter_question: str 