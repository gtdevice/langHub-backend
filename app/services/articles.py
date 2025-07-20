import json
from typing import List, Optional
from supabase import Client
from app.schemas.articles import AdaptedArticleData


async def get_articles(
    supabase: Client,
    category: Optional[str] = None,
    language: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 3
) -> List[AdaptedArticleData]:
    """
    Fetch articles from adapted_articles table with optional filters.
    
    Args:
        supabase: Supabase client instance
        category: Optional category filter
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