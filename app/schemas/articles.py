from pydantic import BaseModel
from typing import Optional


class ArticleListItem(BaseModel):
    articleId: str
    title: str
    introText: str
    thumbnail: str
    category: Optional[str] = None
    language: str
    level: str 