import json
from typing import List, Optional
from supabase import Client
from app.schemas.articles import AdaptedArticleData, DiscoverArticleData
from app.services import get_user_settings


async def get_articles(
    supabase: Client,
    categories: Optional[List[str]] = None,
    language: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 3
) -> List[AdaptedArticleData]:
    """
    Fetch articles from adapted_articles table with optional filters.
    
    Args:
        supabase: Supabase client instance
        categories: Optional category filter
        language: Optional language filter  
        level: Optional level filter
        limit: Maximum number of articles to return (default: 3)
    
    Returns:
        List of ArticleListItem objects
    """
    
    # Build query
    query = supabase.table("adapted_articles").select(
        "id, original_article_id, language, level, title, thumbnail_url, intro, adapted_text, metadata, dialogue_starter_question"
    )
    
    # Apply filters if provided
    if language:
        query = query.eq("language", language)
    if level:
        query = query.eq("level", level)
    if categories:
        query = query.in_("category", categories)
    
    # Execute query with limit
    response = query.limit(limit).execute()
    
    # Transform results to ArticleListItem format
    articles = []
    for row in response.data:
        article = AdaptedArticleData(
            id=row["id"],
            original_article_id=row["original_article_id"],
            language=row["language"],
            level=row["level"],
            title=row["title"],
            thumbnail_url=row["thumbnail_url"],
            intro=row["intro"],
            adapted_text=row["adapted_text"],
            metadata=row["metadata"],
            dialogue_starter_question=row["dialogue_starter_question"]
        )
        articles.append(article)
    
    return articles

# add method to get article by id
async def get_article_by_id(supabase: Client, article_id: int) -> Optional[AdaptedArticleData]:
    """
    Fetch a single article by its ID.

    Args:
        supabase: Supabase client instance
        article_id: ID of the article to fetch

    Returns:
        ArticleListItem object or None if not found
    """

    response = supabase.table("adapted_articles").select(
        "id, original_article_id, language, level, title, thumbnail_url, intro, adapted_text, metadata, dialogue_starter_question"
    ).eq("id", article_id).single().execute()

    if not response.data:
        return None

    row = response.data
    return AdaptedArticleData(
        id=row["id"],
        original_article_id=row["original_article_id"],
        language=row["language"],
        level=row["level"],
        title=row["title"],
        thumbnail_url=row["thumbnail_url"],
        intro=row["intro"],
        adapted_text=row["adapted_text"],
        metadata=json.dumps(row["metadata"]),
        dialogue_starter_question=row["dialogue_starter_question"]
    )

from app.services.dialogs import get_all_dialogs
async def get_discover_articles(
    supabase: Client,
    user_id: Optional[str] = None,
) -> List[DiscoverArticleData]:
    """
    Get user preferences (settings) and fetch articles for discovery with filters.
    get user dialogs and compile everything into DiscoverArticleData
    """
    # Fetch user preferences if user_id is provided
    user_preferences = await get_user_settings(supabase, user_id) if user_id else None

    article_list = await get_articles(supabase,
        categories=user_preferences.preferred_categories if user_preferences else [],
        language=user_preferences.learning_language if user_preferences else None,
        level=user_preferences.language_level if user_preferences else None,
        limit=30
    )
    # List[DialogResponse]
    all_dialogs = await get_all_dialogs(supabase, user_id) if user_id else []
    # Compile DiscoverArticleData from articles and dialogs

    discover_articles = []
    for article in article_list:
        # Find matching dialog for the article
        matching_dialog = next((dialog for dialog in all_dialogs if dialog.article.id == article.id), None)
        # Create DiscoverArticleData entry
        discover_article = DiscoverArticleData(
            title=article.title,
            thumbnail_url=article.thumbnail_url,
            intro=article.intro,
            adapted_article_id=article.id,
            dialogue_id=matching_dialog.dialogId if matching_dialog else None,
            created_at= None
        )
        discover_articles.append(discover_article)

    return discover_articles