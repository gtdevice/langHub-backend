from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from supabase import Client
from app.api.deps import get_current_user_supabase_client, get_current_user
from app.schemas.articles import AdaptedArticleData, DiscoverArticleData
from app.services.articles import get_articles, get_discover_articles
from app.services.user_article_service import UserArticleService

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

@router.post("/generate", response_model=Dict[str, List[Dict[str, Any]]])
async def generate_articles(
    supabase: Client = Depends(get_current_user_supabase_client),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate and assign new articles to the authenticated user.
    
    Returns up to 3 newly assigned articles.
    """
    service = UserArticleService(supabase)
    articles = await service.generate_and_assign_articles(
        user_id=current_user.get("id"),
        count=3
    )
    
    return {"articles": articles}

@router.get("/discover", response_model=List[DiscoverArticleData])
async def discover_articles(
    language: Optional[str] = Query(None, description="Filter by language"),
    level: Optional[str] = Query(None, description="Filter by level"),
    limit: int = Query(20, description="Number of articles to return"),
    offset: int = Query(0, description="Offset for pagination"),
    supabase: Client = Depends(get_current_user_supabase_client),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Discover articles assigned to the current user.
    
    Returns articles specifically assigned to the authenticated user.
    """
    service = UserArticleService(supabase)
    articles = await service.get_user_assigned_articles(
        user_id=current_user.get("id"),
        limit=limit,
        offset=offset
    )
    
    # Convert to DiscoverArticleData format
    return [
        DiscoverArticleData(
            id=article["id"],
            title=article["title"],
            language=article["language"],
            level=article["level"],
            category=article["category"]
        )
        for article in articles
    ]