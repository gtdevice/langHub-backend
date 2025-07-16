from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from supabase import Client
from app.api.deps import get_supabase_client
from app.schemas.articles import ArticleListItem
from app.services.articles import get_articles

router = APIRouter()


@router.get("/", response_model=List[ArticleListItem])
async def get_article_list(
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    level: Optional[str] = Query(None, description="Filter by level"),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get a list of articles with optional filters.
    
    Returns up to 3 articles based on the provided filters.
    """
    articles = await get_articles(
        supabase=supabase,
        category=category,
        language=language,
        level=level
    )
    return articles 