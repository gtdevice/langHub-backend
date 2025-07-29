from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from supabase import Client
from app.api.deps import get_current_user_supabase_client, get_current_user
from app.schemas.articles import AdaptedArticleData, DiscoverArticleData
from app.services.articles import get_articles, get_discover_articles

from typing import Dict, Any, List
router = APIRouter()


@router.get("/", response_model=List[AdaptedArticleData])
async def get_article_list(
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    level: Optional[str] = Query(None, description="Filter by level"),
    supabase: Client = Depends(get_current_user_supabase_client)
):
    """
    Get a list of articles with optional filters.
    
    Returns up to 3 articles based on the provided filters.
    """
    articles = await get_articles(
        supabase=supabase,
        categories=category,
        language=language,
        level=level
    )
    return articles

@router.get("/discover", response_model=List[DiscoverArticleData])
async def discover_articles(
    supabase: Client = Depends(get_current_user_supabase_client),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Discover articles with no filters.
    """
    return await get_discover_articles(supabase=supabase, user_id=current_user.get("id"))