from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from app.schemas.articles import DiscoverArticleData
from app.api.deps import get_authenticated_user
from app.services.user_article_service import UserArticleService

router = APIRouter()

@router.get("/discover", response_model=List[DiscoverArticleData])
async def discover_articles(
        limit: int = Query(5, description="Number of articles to return"),
        offset: int = Query(0, description="Offset for pagination"),
        auth_user = Depends(get_authenticated_user)
):
    """
    Discover articles assigned to the current user.

    Returns articles specifically assigned to the authenticated user.
    """
    service = UserArticleService(auth_user.client)
    discover_articles_list = await service.get_user_assigned_articles(
        user_id=auth_user.user_id,
        limit=limit,
        offset=offset
    )
    return discover_articles_list


@router.post("/generate", response_model=Dict[str, List[Dict[str, Any]]])
async def generate_articles(
        auth_user = Depends(get_authenticated_user)
):
    """
    Generate and assign new articles to the authenticated user.

    Returns up to 3 newly assigned articles.
    """
    service = UserArticleService(auth_user.client)
    articles = await service.generate_and_assign_articles(
        user_id=auth_user.user_id,
        count=3
    )

    return {"articles": articles}